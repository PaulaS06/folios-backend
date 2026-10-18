from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from data.database import get_db
from data.models import Estudiante
from security import leer_token

# auto_error=False: si falta el encabezado, respondemos nosotros con un 401 uniforme.
esquema_bearer = HTTPBearer(auto_error=False)


def estudiante_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(esquema_bearer),
    db: Session = Depends(get_db),
) -> Estudiante:
    """Devuelve el estudiante dueño del token, o responde 401."""
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado o sesión vencida.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credenciales is None:
        raise error

    id_estudiante = leer_token(credenciales.credentials)
    if id_estudiante is None:
        raise error

    estudiante = db.get(Estudiante, id_estudiante)
    if estudiante is None:
        raise error
    return estudiante