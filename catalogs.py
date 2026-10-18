from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from data.database import get_db
from data.models import Programa, Categoria, Materia
from data.schemas import ProgramaRespuesta, CategoriaRespuesta, MateriaRespuesta

# Un router agrupa endpoints relacionados fuera de main.py.
# Los catálogos son públicos: el registro necesita los programas antes de
# que exista una sesión, y no contienen datos de nadie.
router = APIRouter(prefix="/api", tags=["Catálogos"])


@router.get("/programas", response_model=list[ProgramaRespuesta])
def listar_programas(db: Session = Depends(get_db)):
    return db.scalars(select(Programa).order_by(Programa.facultad, Programa.nombre)).all()


@router.get("/categorias", response_model=list[CategoriaRespuesta])
def listar_categorias(db: Session = Depends(get_db)):
    return db.scalars(select(Categoria).order_by(Categoria.nombre)).all()


@router.get("/materias", response_model=list[MateriaRespuesta])
def listar_materias(db: Session = Depends(get_db)):
    # Se devuelven TODAS las materias (no solo las del programa del estudiante),
    # con el nombre de su programa para que el front las agrupe.
    filas = db.execute(
        select(Materia.codigo, Materia.nombre, Programa.nombre.label("programa"))
        .join(Programa, Programa.id == Materia.id_programa)
        .order_by(Programa.nombre, Materia.nombre)
    ).all()
    return [
        {"codigo": f.codigo, "nombre": f.nombre, "programa": f.programa}
        for f in filas
    ]