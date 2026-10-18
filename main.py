from fastapi import FastAPI

app = FastAPI(title="Folios Backend")


@app.get("/")
def hola_mundo():
    return {"mensaje": "Hola mundo desde el backend del proyecto Folios"}