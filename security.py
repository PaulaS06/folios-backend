import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv

load_dotenv()

# SECRET_KEY firma los tokens: quien la tenga puede fabricar sesiones de
# cualquier estudiante. Igual que la contraseña de la BD, vive solo en .env.
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("Falta SECRET_KEY en el archivo .env")

ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 60   # duración de la sesión (decisión ajustable)


# --- Contraseñas ---------------------------------------------------------------
def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except ValueError:
        # Hash con formato inválido: cuenta como "no coincide", no como error 500.
        return False


# --- Tokens --------------------------------------------------------------------
def crear_token(id_estudiante: int) -> str:
    vence = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    payload = {"sub": str(id_estudiante), "exp": vence}   # "sub" debe ser texto
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def leer_token(token: str) -> int | None:
    """Devuelve el id del estudiante si el token es válido y no ha vencido; si no, None."""
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],   # lista fija: nunca confiar en lo que declare el token
            options={"require": ["exp", "sub"]},
        )
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None