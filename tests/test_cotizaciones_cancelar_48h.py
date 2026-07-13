"""Cobertura de la regla de negocio: una cotización solo se puede cancelar con
48h (2+ días, ya que fecha_inicio no tiene hora) de anticipación a la fecha de
inicio vigente (la de la contraoferta si existe, si no la original)."""

from datetime import date, timedelta

from app.models.cotizacion import Cotizacion
from tests.conftest import auth_headers, crear_maquina, crear_usuario

HOY = date.today()


def _crear_cotizacion(
    db_session,
    *,
    maquina,
    arrendatario,
    propietario,
    fecha_inicio: date,
    fecha_fin: date,
    estado: str = "pendiente",
    fecha_inicio_contraoferta: date | None = None,
    fecha_fin_contraoferta: date | None = None,
    precio_contraoferta=None,
) -> Cotizacion:
    cotizacion = Cotizacion(
        maquina_id=maquina.id,
        arrendatario_id=arrendatario.id,
        propietario_id=propietario.id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        precio_propuesto="100.00",
        estado=estado,
        fecha_inicio_contraoferta=fecha_inicio_contraoferta,
        fecha_fin_contraoferta=fecha_fin_contraoferta,
        precio_contraoferta=precio_contraoferta,
    )
    db_session.add(cotizacion)
    db_session.commit()
    db_session.refresh(cotizacion)
    return cotizacion


def _setup(db_session):
    propietario = crear_usuario(db_session, nombre="Dueño", email="dueno@test.com", rol="propietario")
    arrendatario = crear_usuario(db_session, nombre="Inquilino", email="inquilino@test.com", rol="arrendatario")
    maquina = crear_maquina(db_session, propietario=propietario)
    return propietario, arrendatario, maquina


def test_cancelar_permitido_con_48h_o_mas(client, db_session):
    propietario, arrendatario, maquina = _setup(db_session)
    cotizacion = _crear_cotizacion(
        db_session,
        maquina=maquina,
        arrendatario=arrendatario,
        propietario=propietario,
        fecha_inicio=HOY + timedelta(days=2),
        fecha_fin=HOY + timedelta(days=5),
    )

    resp = client.patch(f"/cotizaciones/{cotizacion.id}/cancelar", headers=auth_headers(arrendatario))

    assert resp.status_code == 200
    assert resp.json()["estado"] == "cancelada"


def test_cancelar_bloqueado_con_menos_de_48h(client, db_session):
    propietario, arrendatario, maquina = _setup(db_session)
    cotizacion = _crear_cotizacion(
        db_session,
        maquina=maquina,
        arrendatario=arrendatario,
        propietario=propietario,
        fecha_inicio=HOY + timedelta(days=1),
        fecha_fin=HOY + timedelta(days=5),
    )

    resp = client.patch(f"/cotizaciones/{cotizacion.id}/cancelar", headers=auth_headers(arrendatario))

    assert resp.status_code == 400
    assert "48h" in resp.json()["detail"]
    db_session.refresh(cotizacion)
    assert cotizacion.estado == "pendiente"


def test_cancelar_bloqueado_si_fecha_inicio_ya_paso(client, db_session):
    propietario, arrendatario, maquina = _setup(db_session)
    cotizacion = _crear_cotizacion(
        db_session,
        maquina=maquina,
        arrendatario=arrendatario,
        propietario=propietario,
        fecha_inicio=HOY - timedelta(days=1),
        fecha_fin=HOY + timedelta(days=5),
    )

    resp = client.patch(f"/cotizaciones/{cotizacion.id}/cancelar", headers=auth_headers(arrendatario))

    assert resp.status_code == 400
    db_session.refresh(cotizacion)
    assert cotizacion.estado == "pendiente"


def test_cancelar_usa_fecha_de_contraoferta_no_la_original(client, db_session):
    """La original ya pasó, pero la contraoferta (la fecha vigente) sigue
    teniendo 3 días de margen -> debe permitirse."""
    propietario, arrendatario, maquina = _setup(db_session)
    cotizacion = _crear_cotizacion(
        db_session,
        maquina=maquina,
        arrendatario=arrendatario,
        propietario=propietario,
        fecha_inicio=HOY - timedelta(days=10),
        fecha_fin=HOY - timedelta(days=5),
        estado="contraoferta",
        fecha_inicio_contraoferta=HOY + timedelta(days=3),
        fecha_fin_contraoferta=HOY + timedelta(days=6),
        precio_contraoferta="90.00",
    )

    resp = client.patch(f"/cotizaciones/{cotizacion.id}/cancelar", headers=auth_headers(arrendatario))

    assert resp.status_code == 200
    assert resp.json()["estado"] == "cancelada"


def test_propietario_no_puede_cancelar_cotizacion_de_otro(client, db_session):
    """Regresión: el chequeo de permisos (solo el arrendatario dueño puede
    cancelar) sigue intacto después de agregar la validación de 48h."""
    propietario, arrendatario, maquina = _setup(db_session)
    cotizacion = _crear_cotizacion(
        db_session,
        maquina=maquina,
        arrendatario=arrendatario,
        propietario=propietario,
        fecha_inicio=HOY + timedelta(days=10),
        fecha_fin=HOY + timedelta(days=12),
    )

    resp = client.patch(f"/cotizaciones/{cotizacion.id}/cancelar", headers=auth_headers(propietario))

    assert resp.status_code == 403


def test_no_se_puede_cancelar_cotizacion_ya_aceptada(client, db_session):
    """Regresión: el chequeo de estado (solo pendiente/contraoferta) sigue
    intacto, incluso si tiene 48h+ de margen."""
    propietario, arrendatario, maquina = _setup(db_session)
    cotizacion = _crear_cotizacion(
        db_session,
        maquina=maquina,
        arrendatario=arrendatario,
        propietario=propietario,
        fecha_inicio=HOY + timedelta(days=10),
        fecha_fin=HOY + timedelta(days=12),
        estado="aceptada",
    )

    resp = client.patch(f"/cotizaciones/{cotizacion.id}/cancelar", headers=auth_headers(arrendatario))

    assert resp.status_code == 400
    assert "48h" not in resp.json()["detail"]
