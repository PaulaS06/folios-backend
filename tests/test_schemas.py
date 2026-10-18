import pytest
from pydantic import ValidationError

from data.schemas import AccionCrear, DocumentoCrear, EstudianteRegistro


def datos_registro(**cambios):
    """Datos de registro válidos; cada prueba cambia solo lo que quiere probar."""
    datos = {
        "nombre": "Ana Pérez",
        "correo": "ana@soyudemedellin.edu.co",
        "contrasena": "secreta123",
        "semestre": 6,
        "programa": "Ingeniería de Sistemas",
    }
    datos.update(cambios)
    return datos


# ---------- registro (HU-01) ----------

def test_registro_valido_normaliza_correo_y_nombre():
    estudiante = EstudianteRegistro(**datos_registro(
        nombre="  Ana Pérez  ", correo="  ANA@SoyUdeMedellin.edu.co "))
    assert estudiante.correo == "ana@soyudemedellin.edu.co"
    assert estudiante.nombre == "Ana Pérez"


def test_registro_rechaza_correo_no_institucional():
    with pytest.raises(ValidationError):
        EstudianteRegistro(**datos_registro(correo="ana@gmail.com"))


def test_registro_rechaza_contrasena_corta():
    with pytest.raises(ValidationError):
        EstudianteRegistro(**datos_registro(contrasena="123"))


def test_registro_rechaza_contrasena_de_mas_de_72_bytes():
    # 40 caracteres "ñ" = 80 bytes en UTF-8: pasa el mínimo de caracteres,
    # pero supera el límite de bcrypt, que se mide en BYTES
    with pytest.raises(ValidationError):
        EstudianteRegistro(**datos_registro(contrasena="ñ" * 40))


@pytest.mark.parametrize("semestre", [0, 11])
def test_registro_rechaza_semestre_fuera_de_rango(semestre):
    with pytest.raises(ValidationError):
        EstudianteRegistro(**datos_registro(semestre=semestre))


# ---------- publicar documento (HU-05) ----------

def test_documento_acepta_enlace_https():
    doc = DocumentoCrear(nombre="Parcial 1", id_materia=1, id_categoria=3,
                         enlace="https://drive.google.com/file/d/abc")
    assert doc.enlace.startswith("https://")


def test_documento_rechaza_enlace_javascript():
    # Seguridad: un enlace "javascript:" ejecutaría código al hacer clic
    with pytest.raises(ValidationError):
        DocumentoCrear(nombre="Malicioso", id_materia=1, id_categoria=3,
                       enlace="javascript:alert('hola')")


def test_documento_descripcion_vacia_se_guarda_como_none():
    doc = DocumentoCrear(nombre="Resumen", descripcion="   ", id_materia=1,
                         id_categoria=2, enlace="https://ejemplo.com")
    assert doc.descripcion is None


# ---------- calificar / comentar (HU-07) ----------

def test_accion_rechaza_calificacion_mayor_a_5():
    with pytest.raises(ValidationError):
        AccionCrear(valor=6)


def test_accion_exige_calificacion_o_comentario():
    # Un comentario de solo espacios cuenta como vacío
    with pytest.raises(ValidationError):
        AccionCrear(comentario="   ")


def test_accion_acepta_solo_comentario():
    accion = AccionCrear(comentario="Muy útil")
    assert accion.valor is None
    assert accion.comentario == "Muy útil"