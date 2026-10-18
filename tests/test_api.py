from fastapi.testclient import TestClient

from main import app

# TestClient simula peticiones HTTP a la API sin levantar uvicorn
cliente = TestClient(app)


def test_swagger_disponible():
    # Punto 3 de la entrega: documentación OpenAPI
    assert cliente.get("/docs").status_code == 200
    rutas = cliente.get("/openapi.json").json()["paths"]
    assert "/api/registro" in rutas
    assert "/api/login" in rutas


def test_perfil_sin_token_responde_401():
    respuesta = cliente.get("/api/perfil")
    assert respuesta.status_code == 401


def test_perfil_con_token_falso_responde_401():
    respuesta = cliente.get("/api/perfil", headers={"Authorization": "Bearer token-inventado"})
    assert respuesta.status_code == 401


def test_listar_documentos_sin_sesion_responde_401():
    assert cliente.get("/api/documentos").status_code == 401


def test_registro_con_correo_no_institucional_responde_422():
    respuesta = cliente.post("/api/registro", json={
        "nombre": "Ana", "correo": "ana@gmail.com", "contrasena": "secreta123",
        "semestre": 6, "programa": "Ingeniería de Sistemas",
    })
    assert respuesta.status_code == 422