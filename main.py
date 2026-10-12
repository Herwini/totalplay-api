"""
API REST de TotalPlay: clientes, servicios contratados, reporte y paquetes.

Se ejecuta con:  uvicorn main:app --reload
Documentación (Swagger):  http://localhost:8000/docs

Flujo de cada petición:
    middleware -> endpoint (este archivo) -> reglas_negocio.py -> datos.py
"""

import time
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Path, Query, Request
from fastapi.responses import JSONResponse

import datos
import reglas_negocio
from modelos import ClienteEntrada, PaqueteCosto, ServicioActualizar, ServicioCrear

app = FastAPI(
    title="API TotalPlay",
    description="""
API REST para administrar los clientes de TotalPlay, los paquetes de internet
que contratan y la información para reportes. Reemplaza el Excel que usaba la empresa.

Los datos se guardan en memoria (listas de Python): se pierden al reiniciar el servidor.
""",
    version="1.0.0",
    contact={"name": "Herwin Daniel Velázquez Ábrego"},
    license_info={"name": "MIT"},
)

# ---------------------------------------------------------------------------
# Middleware: se ejecuta en TODAS las peticiones, antes y después del endpoint
# ---------------------------------------------------------------------------
@app.middleware("http")
async def validar_y_medir(request: Request, call_next):
    tiempo_inicio = time.time()

    # Validación: si una petición POST o PUT trae datos, deben venir en JSON.
    if request.method in ("POST", "PUT"):
        trae_datos = request.headers.get("content-length", "0") != "0"
        tipo_contenido = request.headers.get("content-type", "")
        if trae_datos and "application/json" not in tipo_contenido:
            return JSONResponse(
                status_code=415,
                content={"detail": "Los datos deben enviarse en formato JSON"},
            )

    response = await call_next(request)  # aquí se ejecuta el endpoint

    tiempo_total = time.time() - tiempo_inicio
    response.headers["X-Tiempo-Procesamiento"] = f"{tiempo_total:.4f}"
    print(f"{request.method} {request.url.path} -> {response.status_code} ({tiempo_total:.4f} s)")
    return response


# ---------------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------------
@app.get(
    "/v1/api/clientes",
    summary="Consultar todos los clientes",
    tags=["Clientes"],
)
def consultar_clientes():
    return {
        "success": True,
        "total": len(datos.clientes),
        "clientes": datos.clientes,
    }


@app.get(
    "/v1/api/clientes/{id_cliente}",
    summary="Consultar un cliente por id",
    tags=["Clientes"],
)
def consultar_cliente(id_cliente: int = Path(..., ge=1, description="Id del cliente")):
    cliente = reglas_negocio.obtener_cliente_o_404(id_cliente)
    return {"success": True, "cliente": cliente}


@app.post(
    "/v1/api/clientes",
    summary="Registrar un nuevo cliente",
    status_code=201,
    tags=["Clientes"],
)
def registrar_cliente(datos_cliente: ClienteEntrada):
    nuevo_cliente = {
        "id_cliente": datos.siguiente_id(datos.clientes),
        "nombre_cliente": datos_cliente.nombre_cliente,
        "direccion": datos_cliente.direccion,
        "active": True,  # todo cliente nuevo inicia activo
    }
    datos.clientes.append(nuevo_cliente)
    return {"success": True, "mensaje": "Cliente registrado correctamente", "cliente": nuevo_cliente}


@app.put(
    "/v1/api/clientes/{id_cliente}",
    summary="Actualizar la información de un cliente",
    tags=["Clientes"],
)
def actualizar_cliente(
    datos_cliente: ClienteEntrada,
    id_cliente: int = Path(..., ge=1, description="Id del cliente"),
):
    cliente = reglas_negocio.obtener_cliente_o_404(id_cliente)
    cliente["nombre_cliente"] = datos_cliente.nombre_cliente
    cliente["direccion"] = datos_cliente.direccion
    return {"success": True, "mensaje": "Cliente actualizado correctamente", "cliente": cliente}


@app.delete(
    "/v1/api/clientes/{id_cliente}",
    summary="Desactivar un cliente (no se borra)",
    tags=["Clientes"],
)
def desactivar_cliente(id_cliente: int = Path(..., ge=1, description="Id del cliente")):
    cliente = reglas_negocio.obtener_cliente_o_404(id_cliente)
    if not cliente["active"]:
        raise HTTPException(status_code=400, detail="El cliente ya estaba inactivo")
    cliente["active"] = False  # borrado lógico: el registro se queda guardado
    return {"success": True, "mensaje": "Cliente desactivado correctamente", "cliente": cliente}


# ---------------------------------------------------------------------------
# Servicios contratados
# ---------------------------------------------------------------------------
@app.get(
    "/v1/api/servicios",
    summary="Consultar los servicios registrados",
    tags=["Servicios"],
)
def consultar_servicios(
    id_cliente: Optional[int] = Query(None, ge=1, description="Opcional: solo los servicios de este cliente"),
):
    servicios = datos.consumos
    if id_cliente is not None:
        servicios = [s for s in datos.consumos if s["id_cliente"] == id_cliente]
    return {"success": True, "total": len(servicios), "servicios": servicios}


@app.post(
    "/v1/api/servicios",
    summary="Registrar un nuevo servicio",
    status_code=201,
    tags=["Servicios"],
)
def registrar_servicio(datos_servicio: ServicioCrear):
    cliente = reglas_negocio.obtener_cliente_o_404(datos_servicio.id_cliente)
    reglas_negocio.validar_cliente_activo(cliente)

    fecha = datos_servicio.fecha_registro or date.today()  # si no la mandan, hoy
    reglas_negocio.validar_fecha_no_futura(fecha)

    nuevo_servicio = {
        "id_servicio": datos.siguiente_id(datos.consumos),
        "id_cliente": cliente["id_cliente"],
        "paquete": datos_servicio.paquete,
        "fecha_registro": fecha,
    }
    datos.consumos.append(nuevo_servicio)
    return {"success": True, "mensaje": "Servicio registrado correctamente", "servicio": nuevo_servicio}


@app.put(
    "/v1/api/servicios/{id_servicio}",
    summary="Actualizar un servicio existente",
    tags=["Servicios"],
)
def actualizar_servicio(
    datos_servicio: ServicioActualizar,
    id_servicio: int = Path(..., ge=1, description="Id del servicio"),
):
    servicio = reglas_negocio.obtener_servicio_o_404(id_servicio)
    cliente = reglas_negocio.obtener_cliente_o_404(servicio["id_cliente"])
    reglas_negocio.validar_cliente_activo(cliente)

    if datos_servicio.fecha_registro is not None:
        reglas_negocio.validar_fecha_no_futura(datos_servicio.fecha_registro)
        servicio["fecha_registro"] = datos_servicio.fecha_registro

    servicio["paquete"] = datos_servicio.paquete
    return {"success": True, "mensaje": "Servicio actualizado correctamente", "servicio": servicio}


# ---------------------------------------------------------------------------
# Reporte
# ---------------------------------------------------------------------------
@app.get(
    "/v1/api/reportes/servicios",
    summary="Reporte de servicios de clientes activos (filtro por fecha)",
    tags=["Reportes"],
)
def reporte_servicios(
    fecha_inicio: Optional[date] = Query(None, description="Desde esta fecha (AAAA-MM-DD)"),
    fecha_fin: Optional[date] = Query(None, description="Hasta esta fecha (AAAA-MM-DD)"),
):
    reglas_negocio.validar_rango_fechas(fecha_inicio, fecha_fin)

    registros = []
    for servicio in datos.consumos:
        cliente = datos.buscar_cliente(servicio["id_cliente"])

        if not cliente["active"]:
            continue  # el reporte solo muestra clientes activos
        if fecha_inicio and servicio["fecha_registro"] < fecha_inicio:
            continue
        if fecha_fin and servicio["fecha_registro"] > fecha_fin:
            continue

        registros.append({
            "id_servicio": servicio["id_servicio"],
            "paquete": servicio["paquete"],
            "fecha_registro": servicio["fecha_registro"],
            "costo_paquete": reglas_negocio.calcular_costo(servicio["paquete"]),
            "cliente": {
                "id_cliente": cliente["id_cliente"],
                "nombre_cliente": cliente["nombre_cliente"],
                "direccion": cliente["direccion"],
            },
        })

    total_ingresos = sum(r["costo_paquete"] for r in registros)
    return {
        "success": True,
        "total": len(registros),
        "total_ingresos": total_ingresos,
        "registros": registros,
    }


# ---------------------------------------------------------------------------
# Paquetes
# ---------------------------------------------------------------------------
@app.get(
    "/v1/api/paquetes",
    summary="Consultar los paquetes y sus costos",
    tags=["Paquetes"],
)
def consultar_paquetes():
    return {"success": True, "paquetes": datos.paquetes}


@app.put(
    "/v1/api/paquetes/{paquete}",
    summary="Actualizar el costo de un paquete",
    tags=["Paquetes"],
)
def actualizar_costo_paquete(
    nuevo_costo: PaqueteCosto,
    paquete: str = Path(..., description="basico, intermedio o premium"),
):
    paquete = paquete.lower()
    reglas_negocio.validar_paquete_existe(paquete)
    datos.paquetes[paquete] = nuevo_costo.costo
    return {
        "success": True,
        "mensaje": "Costo actualizado correctamente",
        "paquete": paquete,
        "costo": nuevo_costo.costo,
    }
