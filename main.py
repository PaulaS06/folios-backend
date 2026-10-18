from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from catalogs import router as catalogs_router
from data.database import get_db
from documents import router as documents_router
from data.models import Estudiante, Programa
from data.schemas import (
    EstudianteRegistro,
    EstudianteLogin,
    EstudianteRespuesta,
    PerfilRespuesta,
    TokenRespuesta,
)
from security import get_password_hash, verify_password, crear_token
from dependencies import estudiante_actual


app = FastAPI(title="Folios Backend", version="0.1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(catalogs_router)
app.include_router(documents_router)


@app.post(
    "/api/registro",
    response_model=EstudianteRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def registrar_estudiante(datos: EstudianteRegistro, db: Session = Depends(get_db)):
    # Cuando el código llega aquí, Pydantic ya validó formato, dominio del
    # correo, largo de la contraseña y rango del semestre (si no, respondió 422).
    # Lo que queda es lo que solo la base de datos puede saber.

    # 1) RN-01: un correo solo puede tener una cuenta.
    existente = db.scalar(select(Estudiante).where(Estudiante.correo == datos.correo))
    if existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta con ese correo.",
        )

    # 2) El front manda el NOMBRE del programa; la tabla guarda su id.
    programa = db.scalar(select(Programa).where(Programa.nombre == datos.programa))
    if programa is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El programa académico no existe.",
        )

    # 3) RNF-02: solo se guarda el hash, nunca la contraseña original.
    estudiante = Estudiante(
        nombre=datos.nombre,
        correo=datos.correo,
        contrasena=get_password_hash(datos.contrasena),
        semestre=datos.semestre,
        puntaje=0,
        id_programa=programa.id,
    )
    db.add(estudiante)

    # 4) Guardar. El paso 1 evita casi todos los duplicados, pero si dos
    #    registros con el mismo correo llegan al mismo tiempo, el UNIQUE de la
    #    base de datos rechaza al segundo: se atrapa aquí en vez de dar error 500.
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta con ese correo.",
        )

    # 5) refresh() vuelve a leer la fila para traer el id que asignó la base.
    db.refresh(estudiante)

    # 6) response_model=EstudianteRespuesta filtra lo que sale: sin contraseña.
    return estudiante


@app.post("/api/login", response_model=TokenRespuesta)
def iniciar_sesion(datos: EstudianteLogin, db: Session = Depends(get_db)):
    # Pydantic ya normalizó el correo (minúsculas, sin espacios).
    estudiante = db.scalar(select(Estudiante).where(Estudiante.correo == datos.correo))

    # Mismo mensaje si falla el correo o la contraseña: así nadie puede usar
    # el login para averiguar qué correos tienen cuenta.
    if estudiante is None or not verify_password(datos.contrasena, estudiante.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenRespuesta(
        access_token=crear_token(estudiante.id),
        estudiante=EstudianteRespuesta.model_validate(estudiante),
    )


@app.get("/api/perfil", response_model=PerfilRespuesta)
def ver_perfil(
    estudiante: Estudiante = Depends(estudiante_actual),
    db: Session = Depends(get_db),
):
    # Ruta protegida: solo llega aquí quien mande un token válido, y siempre
    # ve SU propio perfil (RF-09): el id sale del token, no de la URL.
    # El estudiante guarda id_programa; para HU-09 (CA_02) se busca el nombre.
    programa = db.get(Programa, estudiante.id_programa) if estudiante.id_programa else None
    return {
        "id": estudiante.id,
        "nombre": estudiante.nombre,
        "correo": estudiante.correo,
        "semestre": estudiante.semestre,
        "puntaje": estudiante.puntaje,
        "programa": programa.nombre if programa else None,
    }