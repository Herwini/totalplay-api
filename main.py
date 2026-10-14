from fastapi import FastAPI, HTTPException, Path, Query
from modelos import ClienteCrear, ServicioCrear, ServicioActualizar, PaqueteActualizar
from datetime import date
from typing import Optional
import time
from fastapi import Request
from fastapi.responses import JSONResponse


app = FastAPI(title="TOTAL PLAY APIRESTTT", description="Esta es una API de ejemplo creada con FastAPI", version="1.0.0")

@app.middleware("http")
async def validar_y_medir_tiempo(request: Request, call_next):
    tiempo_inicio = time.time()

    if request.method in ["POST", "PUT"]:
        trae_datos = request.headers.get("content-length", "0") != "0"
        tipo = request.headers.get("content-type", "")
        if trae_datos and "application/json" not in tipo:
            return JSONResponse(status_code=415, content={"detail": "Los datos deben enviarse en formato JSON"})

    response = await call_next(request)          
    tiempo_total = time.time() - tiempo_inicio
    response.headers["X-Tiempo-Procesamiento"] = f"{tiempo_total:.4f}"
    return response

# Datos en memoria 
clientes = [
    {"id_cliente": 1, "nombre_cliente": "Juan Perez", "direccion": "Av. Constitucion 123", "active": True},
    {"id_cliente": 2, "nombre_cliente": "Ana Lopez", "direccion": "Calle Hidalgo 45", "active": False},
]

consumos = list()

paquetes =  {
        "basico": 400.0,
        "intermedio": 500.0,
        "premium": 600.0
    }

def buscar_cliente_por_id(id_cliente: int):
    for cliente in clientes:
        if cliente["id_cliente"] == id_cliente:
            return cliente
    raise HTTPException(status_code= 404, detail="Cliente no encontrado") 

def validar_cliente_activo(cliente):
    if not cliente["active"]:
        raise HTTPException(status_code=400, detail="El cliente esta inactivo" )

def validar_fecha(fecha):
    if fecha > date.today():
        raise HTTPException(status_code=400, detail="La fecha no puede ser futura")    

def buscar_servicio(id_servicio: int):
    for servicio in consumos:
        if servicio["id_servicio"] == id_servicio:
            return servicio
    raise HTTPException(status_code=404, detail="Servicio no encontrado")
    
    
@app.get("/v1/api/clientes")
def consultar_clientes():
    return {"success": True,    
            "message": f"Consulta de clientes exitosa, total de clientes: {len(clientes)}",
            "data": clientes}

@app.post("/v1/api/clientes", status_code=201)
def registrar_cliente(datos: ClienteCrear):
    nuevo_cliente = {
        "id_cliente": len(clientes) + 1,
        "nombre_cliente": datos.nombre,
        "direccion": datos.direccion,
        "active": True
    }
    clientes.append(nuevo_cliente)
    return {"success": True,    
            "message": f"Registro de cliente exitoso, total de clientes: {nuevo_cliente}",
            "data": nuevo_cliente}

@app.get("/v1/api/clientes/{id_cliente}")
def consultar_cliente(id_cliente: int = Path(..., ge=1, description="Id del cliente")):
    cliente = buscar_cliente_por_id(id_cliente)
    return {
        "success": True,
        "cliente": cliente
    }

@app.put("/v1/api/clientes/{id_cliente}")
def actualizar_cliente(datos: ClienteCrear, id_cliente: int = Path(..., ge=1, description="id del cliente")):
    cliente = buscar_cliente_por_id(id_cliente)
    cliente["nombre_cliente"] = datos.nombre
    cliente["direccion"] = datos.direccion
    return {"success": True,
            "mensaje": "Cliente actualizado",
            "cliente": cliente}

@app.delete("/v1/api/clientes/{id_cliente}")
def desactivar_cliente(id_cliente: int = Path(..., ge=1, description="id del cliente")):
    cliente = buscar_cliente_por_id(id_cliente)
    if not cliente["active"]:
        raise HTTPException(status_code=400, detail="El cliente ya estaba inactivo")
    cliente["active"] = False
    return {"success": True,
            "mensaje": "Cliente desactivado",
            "cliente": cliente}

@app.post("/v1/api/servicios", status_code=201)
def registrar_servicio(datos: ServicioCrear):
    cliente = buscar_cliente_por_id(datos.id_cliente)
    validar_cliente_activo(cliente)

    fecha = datos.fecha_registro 
    if fecha is None:
        fecha = date.today()
    validar_fecha(fecha)

    servicio = {
        "id_servicio": len(consumos) + 1,
        "id_cliente": cliente["id_cliente"],
        "paquete": datos.paquete,
        "fecha_registro": fecha
    }

    consumos.append(servicio)
    return {
        "success": True,
        "mensaje": "Servicio registrado",
        "servicio": servicio
    }

@app.get("/v1/api/servicios")
def consultar_servicios(id_cliente: Optional[int] = Query(None, ge=1, description="Filtrar por cliente")):
    resultado = consumos
    if id_cliente is not None:
        resultado = [s for s in consumos if s["id_cliente"] == id_cliente]
    return {
        "success": True,
        "total": len(resultado),
        "servicios": resultado
    }   

@app.put("/v1/api/servicios/{id_servicio}")
def actualizar_servicio(datos: ServicioActualizar, id_servicio: int):
    servicio = buscar_servicio(id_servicio)
    cliente = buscar_cliente_por_id(servicio["id_cliente"])
    validar_cliente_activo(cliente)

    if datos.fecha_registro is not None:
        validar_fecha(datos.fecha_registro)
        servicio["fecha_registro"] = datos.fecha_registro
    servicio["paquete"] = datos.paquete
    return {
        "success": True,
        "mensaje": "Servicio actualizado",
        "servicio": servicio
    }

@app.get("/v1/api/reportes/servicios")
def reporte_servicios(
    fecha_inicio: Optional[date] = Query(None, description="Desde (AAAA-MM-DD)"),
    fecha_fin: Optional[date] = Query(None, description="Hasta (AAAA-MM-DD)"),
):
    if fecha_inicio is not None and fecha_fin is not None and fecha_inicio > fecha_fin:
        raise HTTPException(status_code=400, detail="La fecha de inicio no puede ser mayor que la final")

    registros = []
    for servicio in consumos:
        cliente = buscar_cliente_por_id(servicio["id_cliente"])
        if not cliente["active"]:
            continue                                   # solo clientes activos
        if fecha_inicio is not None and servicio["fecha_registro"] < fecha_inicio:
            continue                                   # antes del rango
        if fecha_fin is not None and servicio["fecha_registro"] > fecha_fin:
            continue                                   # después del rango
        registros.append({
            "paquete": servicio["paquete"],
            "fecha_registro": servicio["fecha_registro"],
            "costo_paquete": paquetes[servicio["paquete"]],   # precio actual del paquete
            "cliente": cliente,
        })

    total_ingresos = 0
    for registro in registros:
        total_ingresos = total_ingresos + registro["costo_paquete"]

    return {
        "success": True, 
        "total": len(registros), 
        "total_ingresos": total_ingresos, 
        "registros": registros}

@app.get("/v1/api/paquetes")
def consultar_paquetes():
    return {"success": True, "paquetes": paquetes}


@app.put("/v1/api/paquetes/{paquete}")
def actualizar_costo(datos: PaqueteActualizar, paquete: str = Path(..., description="basico, intermedio o premium")):
    paquete = paquete.lower()
    if paquete not in paquetes:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    paquetes[paquete] = datos.costo
    return {"success": True, "mensaje": "Costo actualizado", "paquete": paquete, "costo": datos.costo}

