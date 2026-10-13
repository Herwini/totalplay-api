# API TotalPlay

API REST para administrar los clientes de TotalPlay, los paquetes de internet que contratan y la información para reportes. Sustituye el Excel que usaba la empresa.

Actividad del 2.º parcial (Fase 2) de **Tecnologías Web Servidor**.
Autor: Herwin Daniel Velázquez Ábrego.

## Objetivo

Construir una API REST con Python, FastAPI y Pydantic que registre, consulte y actualice clientes y servicios, aplique las reglas de negocio de TotalPlay y responda siempre en JSON con los códigos HTTP adecuados.

## Alcance

- **Clientes:** consultar, registrar, actualizar y desactivar (borrado lógico con `active = false`).
- **Servicios contratados:** registrar, consultar y actualizar el paquete de un cliente.
- **Reporte:** servicios de clientes activos con su costo, filtrables por rango de fechas.
- **Paquetes:** consultar y actualizar el costo de cada paquete.
- Sin base de datos: la información vive en listas de Python y se pierde al reiniciar el servidor (comportamiento esperado).

## Tecnologías

Python 3, FastAPI, Pydantic, Uvicorn, JSON y Swagger (`/docs`).

## Estructura del proyecto

```
totalplay-api/
├── main.py           # App de FastAPI, middleware, datos en memoria, reglas de negocio y endpoints
├── modelos.py        # Modelos de Pydantic: lo que la API recibe y lo que devuelve
├── requirements.txt  # Librerías necesarias
└── README.md
```

## Arquitectura

El proyecto separa dos responsabilidades principales:

| Archivo | Responsabilidad |
|---|---|
| `modelos.py` | Define con Pydantic la estructura de los datos que **recibe** la API (`ClienteCrear`, `ServicioCrear`, ...) y de los que **devuelve** (`ClienteRespuesta`, `ReporteRespuesta`, ...). |
| `main.py` | Configura la aplicación, el middleware, guarda los datos en listas, aplica las reglas de negocio con funciones reutilizables y define los endpoints. |

Flujo de una petición:

```
Cliente (Swagger/Postman) -> Middleware -> Pydantic valida el body (modelos.py)
    -> Endpoint (main.py) -> Reglas de negocio -> Listas en memoria
    -> Respuesta JSON validada con response_model
```

El **middleware** se ejecuta en todas las peticiones:
1. Valida que las peticiones `POST` y `PUT` que traen datos los envíen en JSON (si no, responde `415`).
2. Mide cuánto tarda cada petición y lo agrega en el encabezado `X-Tiempo-Procesamiento`.

## Instalación y ejecución (Windows)

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

En macOS o Linux el entorno se activa con `source .venv/bin/activate`.

Con el servidor encendido, abre **http://localhost:8000/docs** para probar la API en Swagger.

## Endpoints

| Método | URL | Descripción |
|---|---|---|
| GET | `/v1/api/clientes` | Consultar todos los clientes (success, total y lista) |
| GET | `/v1/api/clientes/{id_cliente}` | Consultar un cliente |
| POST | `/v1/api/clientes` | Registrar un cliente |
| PUT | `/v1/api/clientes/{id_cliente}` | Actualizar nombre y dirección |
| DELETE | `/v1/api/clientes/{id_cliente}` | Desactivar un cliente (`active = false`) |
| GET | `/v1/api/servicios` | Consultar servicios (filtro opcional `?id_cliente=`) |
| POST | `/v1/api/servicios` | Registrar un servicio |
| PUT | `/v1/api/servicios/{id_servicio}` | Actualizar un servicio |
| GET | `/v1/api/reportes/servicios` | Reporte de clientes activos (`?fecha_inicio=&fecha_fin=`) |
| GET | `/v1/api/paquetes` | Consultar paquetes y costos |
| PUT | `/v1/api/paquetes/{paquete}` | Actualizar el costo de un paquete |

## Reglas de negocio

- Los clientes no se eliminan físicamente: se desactivan con `active = false` y el registro se conserva.
- Solo se registran servicios para clientes activos.
- No se puede actualizar un servicio cuyo cliente esté inactivo.
- Se valida que el cliente, el servicio y el paquete existan.
- El paquete debe ser `basico`, `intermedio` o `premium`.
- La fecha de registro se genera automáticamente si no se envía y no puede ser futura.
- El costo de un paquete debe ser mayor a 0; los nuevos costos se usan en los cálculos posteriores.
- El reporte solo incluye clientes activos y calcula el costo según el paquete contratado.

## Códigos de respuesta

| Código | Cuándo |
|---|---|
| 200 | Consulta, actualización o desactivación correcta |
| 201 | Registro creado (cliente o servicio) |
| 400 | La petición rompe una regla de negocio (cliente inactivo, fecha futura, rango de fechas invertido, cliente ya desactivado) |
| 404 | El cliente, servicio o paquete no existe |
| 415 | Los datos no se enviaron en formato JSON (middleware) |
| 422 | Datos inválidos detectados por Pydantic (campo faltante, tipo incorrecto, paquete no válido, fecha inválida, costo negativo) |

## Ejemplos de prueba

Registrar un cliente (`POST /v1/api/clientes`):

```json
{
  "nombre_cliente": "Juan Pérez López",
  "direccion": "Av. Constitución 123, Monterrey, N.L."
}
```

Registrar un servicio (`POST /v1/api/servicios`):

```json
{
  "id_cliente": 1,
  "paquete": "premium",
  "fecha_registro": "2026-10-12"
}
```

Actualizar el costo de un paquete (`PUT /v1/api/paquetes/premium`):

```json
{
  "costo": 650
}
```
