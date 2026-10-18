from sqlalchemy import Column, Integer, String, Text, Date, Numeric, ForeignKey, UniqueConstraint
from data.database import Base


class Programa(Base):
    __tablename__ = "programa"

    id = Column(Integer, primary_key = True)
    nombre = Column(String)
    facultad = Column(String)


class Estudiante(Base):
    __tablename__ = "estudiante"

    id = Column(Integer, primary_key = True)
    nombre = Column(String)
    correo = Column(String)
    contrasena = Column("contraseña", String)
    semestre = Column(Integer)
    puntaje = Column(Integer)
    id_programa = Column(Integer, ForeignKey("programa.id"))


class Materia(Base):
    __tablename__ = "materia"

    codigo = Column(Integer, primary_key = True)
    nombre = Column(String)
    id_programa = Column(Integer, ForeignKey("programa.id"))


class Categoria(Base):
    __tablename__ = "categoria"

    id = Column(Integer, primary_key = True)
    nombre = Column(String)


class Documento(Base):
    __tablename__ = "documento"

    id = Column(Integer, primary_key = True)
    nombre = Column(String)
    descripcion = Column(Text)
    enlace_archivo = Column(String)
    id_materia = Column(Integer, ForeignKey("materia.codigo"))
    id_estudiante = Column(Integer, ForeignKey("estudiante.id"))
    promedio_calificacion = Column(Numeric)
    fecha_subida = Column(Date)
    descargas_totales = Column(Integer)
    id_categoria = Column(Integer, ForeignKey("categoria.id"))


class Accion(Base):
    """Calificación y/o comentario de un estudiante sobre un documento."""
    __tablename__ = "accion"
    # Refleja la restricción de la BD: un registro por (estudiante, documento).
    __table_args__ = (
        UniqueConstraint("id_estudiante", "id_documento", name = "uq_accion_estudiante_documento"),
    )

    id = Column(Integer, primary_key = True)
    valor = Column(Numeric(2, 1))          # 1 a 5; puede ser NULL si solo comenta
    comentario = Column(Text)              # puede ser NULL si solo califica
    fecha_calificacion = Column(Date)      # la BD la llena con CURRENT_DATE
    id_estudiante = Column(Integer, ForeignKey("estudiante.id"))
    id_documento = Column(Integer, ForeignKey("documento.id", ondelete = "CASCADE"))