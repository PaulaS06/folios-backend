import os
import sys
from pathlib import Path

# 1) Que las pruebas puedan hacer "import security" o "from main import app".
#    Este archivo vive en tests/, así que la raíz del proyecto es la carpeta de arriba.
#    (Antes lo hacía el pytest.ini con "pythonpath = .")
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_PROYECTO))

# 2) Variables de entorno FALSAS para las pruebas. Se definen antes de importar
#    el código, para que security.py y database.py no usen las del .env real.
#    load_dotenv() no sobrescribe variables que ya existen, así que las pruebas
#    nunca tocan la base de datos de verdad.
os.environ.setdefault("DATABASE_URL", "postgresql://prueba:prueba@localhost:5432/prueba")
os.environ.setdefault("SECRET_KEY", "clave-solo-para-pruebas-con-mas-de-32-bytes")