from fastapi import FastAPI, HTTPException, Path
from modelos import ClienteCrear


app = FastAPI(title="TOTAL PLAY APIRESTTT", description="Esta es una API de ejemplo creada con FastAPI", version="1.0.0")


# Datos en memoria (se pierden al reiniciar el servidor)
clientes = [
    {"id_cliente": 1, "nombre_cliente": "Juan Perez", "direccion": "Av. Constitucion 123", "active": True},
    {"id_cliente": 2, "nombre_cliente": "Ana Lopez", "direccion": "Calle Hidalgo 45", "active": False},
]

def buscar_cliente_por_id(id_cliente: int):
    for cliente in clientes:
        if cliente["id_cliente"] == id_cliente:
            return cliente
    raise HTTPException(status_code= 404, detail="Cliente no encontrado") 

@app.get("/v1/api/clientes")
def consultar_clientes():
    return {"success": True,    
            "message": f"Consulta de clientes exitosa, total de clientes: {len(clientes)}",
            "data": clientes}

@app.post("/v1/api/clientes")
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





                       