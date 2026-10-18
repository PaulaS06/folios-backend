from datetime import datetime, timedelta, timezone

import jwt

import security
from security import crear_token, get_password_hash, leer_token, verify_password


# ---------- contraseñas (RNF-02: solo se guarda el hash) ----------

def test_hash_no_guarda_la_contrasena_original():
    hash_generado = get_password_hash("secreta123")
    assert hash_generado != "secreta123"


def test_verificar_contrasena_correcta():
    hash_generado = get_password_hash("secreta123")
    assert verify_password("secreta123", hash_generado) is True


def test_verificar_contrasena_incorrecta():
    hash_generado = get_password_hash("secreta123")
    assert verify_password("otra-clave", hash_generado) is False


def test_hash_con_formato_invalido_no_revienta():
    # Debe responder "no coincide", no lanzar un error (que sería un 500)
    assert verify_password("secreta123", "esto-no-es-un-hash") is False


# ---------- tokens JWT (sesión, HU-02) ----------

def test_token_valido_devuelve_el_id_del_estudiante():
    token = crear_token(5)
    assert leer_token(token) == 5


def test_token_alterado_es_rechazado():
    token = crear_token(5)
    token_alterado = token[:-2] + ("aa" if not token.endswith("aa") else "bb")
    assert leer_token(token_alterado) is None


def test_token_vencido_es_rechazado():
    vencido = datetime.now(timezone.utc) - timedelta(minutes=1)
    token = jwt.encode({"sub": "5", "exp": vencido}, security.SECRET_KEY, algorithm="HS256")
    assert leer_token(token) is None


def test_token_firmado_con_otra_clave_es_rechazado():
    vence = datetime.now(timezone.utc) + timedelta(minutes=10)
    token = jwt.encode({"sub": "5", "exp": vence}, "clave-de-un-atacante", algorithm="HS256")
    assert leer_token(token) is None