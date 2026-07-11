"""Cobertura del fix de permisos: un propietario debe poder ver los alquileres
de sus propias máquinas (listado y detalle), sin abrir acceso a terceros sin
relación con el alquiler."""

from tests.conftest import auth_headers, crear_alquiler, crear_maquina, crear_usuario


def _setup_escenario(db_session):
    """Propietario dueño de la máquina, arrendatario que la alquiló, y un
    tercero sin ninguna relación con ese alquiler."""
    propietario = crear_usuario(db_session, nombre="Dueño", email="dueno@test.com", rol="propietario")
    arrendatario = crear_usuario(db_session, nombre="Inquilino", email="inquilino@test.com", rol="arrendatario")
    tercero = crear_usuario(db_session, nombre="Tercero", email="tercero@test.com", rol="arrendatario")
    maquina = crear_maquina(db_session, propietario=propietario)
    alquiler = crear_alquiler(db_session, maquina=maquina, arrendatario=arrendatario)
    return propietario, arrendatario, tercero, maquina, alquiler


def test_propietario_ve_alquileres_de_su_maquina_con_rol_propietario(client, db_session):
    propietario, _arrendatario, _tercero, _maquina, alquiler = _setup_escenario(db_session)

    resp = client.get("/alquileres/?rol=propietario", headers=auth_headers(propietario))

    assert resp.status_code == 200
    ids = [a["id"] for a in resp.json()]
    assert alquiler.id in ids


def test_default_sigue_siendo_solo_arrendatario_propio(client, db_session):
    """Sin el query param `rol`, el comportamiento no cambia: un propietario
    que no es arrendatario de nada sigue viendo una lista vacía."""
    propietario, arrendatario, _tercero, _maquina, alquiler = _setup_escenario(db_session)

    resp_propietario = client.get("/alquileres/", headers=auth_headers(propietario))
    assert resp_propietario.status_code == 200
    assert resp_propietario.json() == []

    resp_arrendatario = client.get("/alquileres/", headers=auth_headers(arrendatario))
    assert resp_arrendatario.status_code == 200
    ids = [a["id"] for a in resp_arrendatario.json()]
    assert alquiler.id in ids


def test_rol_todos_incluye_ambas_perspectivas(client, db_session):
    propietario, arrendatario, _tercero, maquina, alquiler = _setup_escenario(db_session)

    # El propietario también alquila una máquina ajena, para confirmar que
    # rol=todos junta "soy dueño" y "soy arrendatario" sin duplicar ni perder filas.
    otro_propietario = crear_usuario(db_session, nombre="Otro Dueño", email="otro@test.com", rol="propietario")
    otra_maquina = crear_maquina(db_session, propietario=otro_propietario, nombre="Grúa Test")
    alquiler_como_arrendatario = crear_alquiler(db_session, maquina=otra_maquina, arrendatario=propietario)

    resp = client.get("/alquileres/?rol=todos", headers=auth_headers(propietario))

    assert resp.status_code == 200
    ids = {a["id"] for a in resp.json()}
    assert ids == {alquiler.id, alquiler_como_arrendatario.id}


def test_propietario_puede_ver_detalle_de_alquiler_de_su_maquina(client, db_session):
    propietario, _arrendatario, _tercero, maquina, alquiler = _setup_escenario(db_session)

    resp = client.get(f"/alquileres/{alquiler.id}", headers=auth_headers(propietario))

    assert resp.status_code == 200
    cuerpo = resp.json()
    assert cuerpo["id"] == alquiler.id
    assert cuerpo["propietario_id"] == propietario.id


def test_arrendatario_sigue_viendo_el_detalle_de_su_propio_alquiler(client, db_session):
    _propietario, arrendatario, _tercero, _maquina, alquiler = _setup_escenario(db_session)

    resp = client.get(f"/alquileres/{alquiler.id}", headers=auth_headers(arrendatario))

    assert resp.status_code == 200
    assert resp.json()["id"] == alquiler.id


def test_tercero_sin_relacion_recibe_403_en_detalle(client, db_session):
    _propietario, _arrendatario, tercero, _maquina, alquiler = _setup_escenario(db_session)

    resp = client.get(f"/alquileres/{alquiler.id}", headers=auth_headers(tercero))

    assert resp.status_code == 403
