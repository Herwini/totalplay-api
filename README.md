# API TotalPlay

API REST para administrar los clientes de TotalPlay, los paquetes de internet que contratan y la información para reportes. Sustituye el Excel que usaba la empresa.
Autor: Herwin Daniel Velázquez Ábrego.

## Tecnologías

Python 3, FastAPI, Pydantic, Uvicorn, JSON y Swagger (`/docs`).

## Instalación y ejecución 

```bash
# 1. Clonar el repositorio y entrar a la carpeta
git clone <URL-del-repositorio>
cd totalplay-api

# 2. Crear y activar el entorno virtual
python -m venv .venv
.venv\Scripts\activate

# 3. Instalar las librerías
pip install -r requirements.txt

# 4. Iniciar el servidor
uvicorn main:app --reload
```

