# 1. Imagen base: Python 3.12 en versión "slim" (Debian mínimo, más liviana)
FROM python:3.12-slim

# 2. Carpeta de trabajo dentro del contenedor
WORKDIR /app

# 3. Primero SOLO el requirements.txt, y se instalan las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Después el resto del código
COPY . .

# 5. Documenta el puerto en que escucha la API
EXPOSE 8000

# 6. Comando que se ejecuta al arrancar el contenedor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]