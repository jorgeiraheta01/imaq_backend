from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.auth import obtener_usuario_actual
from app.database import get_db
from app.models.alquiler import Alquiler
from app.models.cotizacion import Cotizacion
from app.models.maquina import Maquina
from app.models.usuario import Usuario
from app.rate_limit import limiter
from app.schemas.cotizacion import (
    CotizacionContraoferta,
    CotizacionCreate,
    CotizacionOut,
    CotizacionRechazar,
)

router = APIRouter(prefix="/cotizaciones", tags=["Cotizaciones"])

EXPIRACION_HORAS = 72
ESTADOS_ABIERTOS = ("pendiente", "contraoferta")


def _expirar_si_corresponde(cotizacion: Cotizacion, db: Session) -> None:
    """Marca la cotización como expirada si pasaron más de 72h sin respuesta.
    No hay cron: se evalúa perezosamente cada vez que se lee/actualiza una fila."""
    if (
        cotizacion.estado in ESTADOS_ABIERTOS
        and cotizacion.fecha_expiracion is not None
        and cotizacion.fecha_expiracion < datetime.utcnow()
    ):
        cotizacion.estado = "expirada"
        db.commit()
        db.refresh(cotizacion)


def _obtener_cotizacion_o_404(cotizacion_id: int, db: Session) -> Cotizacion:
    cotizacion = db.query(Cotizacion).filter(Cotizacion.id == cotizacion_id).first()
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    _expirar_si_corresponde(cotizacion, db)
    return cotizacion


def _verificar_solapamiento(maquina_id: int, fecha_inicio, fecha_fin, db: Session) -> bool:
    """Devuelve True si hay un alquiler ya confirmado (pendiente/activo) para la
    misma máquina con fechas que se cruzan. Solo se usa como advertencia."""
    conflicto = (
        db.query(Alquiler)
        .filter(
            Alquiler.maquina_id == maquina_id,
            Alquiler.estado.in_(["pendiente", "activo"]),
            Alquiler.fecha_inicio <= fecha_fin,
            Alquiler.fecha_fin >= fecha_inicio,
        )
        .first()
    )
    return conflicto is not None


def _construir_salida(cotizacion: Cotizacion, conflicto_fechas: bool = False) -> CotizacionOut:
    """Serializa incluyendo el nombre/teléfono del arrendatario (para que el
    propietario sepa quién cotiza y pueda avisarle por WhatsApp al aceptar)."""
    return CotizacionOut(
        id=cotizacion.id,
        maquina_id=cotizacion.maquina_id,
        arrendatario_id=cotizacion.arrendatario_id,
        propietario_id=cotizacion.propietario_id,
        fecha_inicio=cotizacion.fecha_inicio,
        fecha_fin=cotizacion.fecha_fin,
        precio_propuesto=cotizacion.precio_propuesto,
        notas=cotizacion.notas,
        estado=cotizacion.estado,
        precio_contraoferta=cotizacion.precio_contraoferta,
        fecha_inicio_contraoferta=cotizacion.fecha_inicio_contraoferta,
        fecha_fin_contraoferta=cotizacion.fecha_fin_contraoferta,
        notas_contraoferta=cotizacion.notas_contraoferta,
        motivo_rechazo=cotizacion.motivo_rechazo,
        alquiler_id=cotizacion.alquiler_id,
        visto=cotizacion.visto,
        fecha_creacion=cotizacion.fecha_creacion,
        fecha_respuesta=cotizacion.fecha_respuesta,
        fecha_expiracion=cotizacion.fecha_expiracion,
        arrendatario_nombre=cotizacion.arrendatario.nombre,
        arrendatario_telefono=cotizacion.arrendatario.telefono,
        conflicto_fechas=conflicto_fechas,
    )


@router.post("/", response_model=CotizacionOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
def crear_cotizacion(
    request: Request,
    datos: CotizacionCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    maquina = db.query(Maquina).filter(Maquina.id == datos.maquina_id).first()
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    if maquina.propietario_id == usuario_actual.id:
        raise HTTPException(status_code=400, detail="No puedes cotizar tu propia máquina")

    dias = (datos.fecha_fin - datos.fecha_inicio).days
    if dias <= 0:
        raise HTTPException(status_code=400, detail="El rango de fechas no es válido")

    nueva_cotizacion = Cotizacion(
        **datos.model_dump(),
        arrendatario_id=usuario_actual.id,
        propietario_id=maquina.propietario_id,
        estado="pendiente",
        visto=False,
        fecha_expiracion=datetime.utcnow() + timedelta(hours=EXPIRACION_HORAS),
    )
    db.add(nueva_cotizacion)
    db.commit()
    db.refresh(nueva_cotizacion)
    return _construir_salida(nueva_cotizacion)


@router.get("/enviadas", response_model=list[CotizacionOut])
def listar_cotizaciones_enviadas(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    cotizaciones = db.query(Cotizacion).filter(Cotizacion.arrendatario_id == usuario_actual.id).all()
    for c in cotizaciones:
        _expirar_si_corresponde(c, db)
        if not c.visto:
            c.visto = True
    db.commit()
    return [_construir_salida(c) for c in cotizaciones]


@router.get("/recibidas", response_model=list[CotizacionOut])
def listar_cotizaciones_recibidas(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    cotizaciones = db.query(Cotizacion).filter(Cotizacion.propietario_id == usuario_actual.id).all()
    for c in cotizaciones:
        _expirar_si_corresponde(c, db)
        if not c.visto:
            c.visto = True
    db.commit()
    return [_construir_salida(c) for c in cotizaciones]


@router.patch("/{cotizacion_id}/aceptar", response_model=CotizacionOut)
def aceptar_cotizacion(
    cotizacion_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    cotizacion = _obtener_cotizacion_o_404(cotizacion_id, db)

    if cotizacion.estado == "pendiente":
        if usuario_actual.id != cotizacion.propietario_id:
            raise HTTPException(status_code=403, detail="Solo el propietario puede aceptar esta cotización")
        fecha_inicio_final = cotizacion.fecha_inicio
        fecha_fin_final = cotizacion.fecha_fin
        precio_final = cotizacion.precio_propuesto
    elif cotizacion.estado == "contraoferta":
        if usuario_actual.id != cotizacion.arrendatario_id:
            raise HTTPException(status_code=403, detail="Solo el arrendatario puede aceptar la contraoferta")
        fecha_inicio_final = cotizacion.fecha_inicio_contraoferta
        fecha_fin_final = cotizacion.fecha_fin_contraoferta
        precio_final = cotizacion.precio_contraoferta
    else:
        raise HTTPException(status_code=400, detail=f"No se puede aceptar una cotización en estado '{cotizacion.estado}'")

    conflicto_fechas = _verificar_solapamiento(cotizacion.maquina_id, fecha_inicio_final, fecha_fin_final, db)

    dias = (fecha_fin_final - fecha_inicio_final).days
    nuevo_alquiler = Alquiler(
        maquina_id=cotizacion.maquina_id,
        arrendatario_id=cotizacion.arrendatario_id,
        fecha_inicio=fecha_inicio_final,
        fecha_fin=fecha_fin_final,
        precio_acordado=precio_final,
        costo_total=dias * precio_final,
        estado="pendiente",
    )
    db.add(nuevo_alquiler)
    db.flush()

    cotizacion.estado = "aceptada"
    cotizacion.alquiler_id = nuevo_alquiler.id
    cotizacion.fecha_respuesta = datetime.utcnow()
    cotizacion.visto = False
    db.commit()
    db.refresh(cotizacion)

    return _construir_salida(cotizacion, conflicto_fechas=conflicto_fechas)


@router.patch("/{cotizacion_id}/rechazar", response_model=CotizacionOut)
def rechazar_cotizacion(
    cotizacion_id: int,
    datos: CotizacionRechazar,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    cotizacion = _obtener_cotizacion_o_404(cotizacion_id, db)

    if cotizacion.estado == "pendiente":
        if usuario_actual.id != cotizacion.propietario_id:
            raise HTTPException(status_code=403, detail="Solo el propietario puede rechazar esta cotización")
    elif cotizacion.estado == "contraoferta":
        if usuario_actual.id != cotizacion.arrendatario_id:
            raise HTTPException(status_code=403, detail="Solo el arrendatario puede rechazar la contraoferta")
    else:
        raise HTTPException(status_code=400, detail=f"No se puede rechazar una cotización en estado '{cotizacion.estado}'")

    cotizacion.estado = "rechazada"
    cotizacion.motivo_rechazo = datos.motivo_rechazo
    cotizacion.fecha_respuesta = datetime.utcnow()
    cotizacion.visto = False
    db.commit()
    db.refresh(cotizacion)
    return _construir_salida(cotizacion)


@router.patch("/{cotizacion_id}/contraoferta", response_model=CotizacionOut)
def contraofertar_cotizacion(
    cotizacion_id: int,
    datos: CotizacionContraoferta,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    cotizacion = _obtener_cotizacion_o_404(cotizacion_id, db)

    if usuario_actual.id != cotizacion.propietario_id:
        raise HTTPException(status_code=403, detail="Solo el propietario puede hacer una contraoferta")
    if cotizacion.estado != "pendiente":
        raise HTTPException(status_code=400, detail=f"No se puede contraofertar una cotización en estado '{cotizacion.estado}'")

    dias = (datos.fecha_fin_contraoferta - datos.fecha_inicio_contraoferta).days
    if dias <= 0:
        raise HTTPException(status_code=400, detail="El rango de fechas no es válido")

    cotizacion.estado = "contraoferta"
    cotizacion.precio_contraoferta = datos.precio_contraoferta
    cotizacion.fecha_inicio_contraoferta = datos.fecha_inicio_contraoferta
    cotizacion.fecha_fin_contraoferta = datos.fecha_fin_contraoferta
    cotizacion.notas_contraoferta = datos.notas_contraoferta
    cotizacion.fecha_respuesta = datetime.utcnow()
    cotizacion.visto = False
    db.commit()
    db.refresh(cotizacion)
    return _construir_salida(cotizacion)


@router.patch("/{cotizacion_id}/cancelar", response_model=CotizacionOut)
def cancelar_cotizacion(
    cotizacion_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    cotizacion = _obtener_cotizacion_o_404(cotizacion_id, db)

    if usuario_actual.id != cotizacion.arrendatario_id:
        raise HTTPException(status_code=403, detail="Solo el arrendatario que la creó puede cancelarla")
    if cotizacion.estado not in ESTADOS_ABIERTOS:
        raise HTTPException(status_code=400, detail=f"No se puede cancelar una cotización en estado '{cotizacion.estado}'")

    cotizacion.estado = "cancelada"
    cotizacion.fecha_respuesta = datetime.utcnow()
    cotizacion.visto = False
    db.commit()
    db.refresh(cotizacion)
    return _construir_salida(cotizacion)


@router.get("/no-vistas/count")
def contar_no_vistas(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """Conteo para el badge del navbar: cotizaciones recibidas pendientes sin
    ver, más contraofertas enviadas sin ver."""
    recibidas = (
        db.query(Cotizacion)
        .filter(
            Cotizacion.propietario_id == usuario_actual.id,
            Cotizacion.visto.is_(False),
            Cotizacion.estado == "pendiente",
        )
        .count()
    )
    enviadas = (
        db.query(Cotizacion)
        .filter(
            Cotizacion.arrendatario_id == usuario_actual.id,
            Cotizacion.visto.is_(False),
            Cotizacion.estado == "contraoferta",
        )
        .count()
    )
    return {"total": recibidas + enviadas}
