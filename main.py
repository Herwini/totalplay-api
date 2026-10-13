import time
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Path, Query, Request
from fastapi.responses import JSONResponse

from modelos import (
    ClienteActualizar,
    ClienteCrear,
    ClienteOperacionRespuesta,
    ClienteReporte,
    ClienteRespuesta,
    ListaClientesRespuesta,
    ListaPaquetesRespuesta,
    ListaServiciosRespuesta,
    PaqueteActualizar,
    PaqueteRespuesta,
    RegistroReporte,
    ReporteRespuesta,
    ServicioActualizar,
    ServicioCrear,
    ServicioOperacionRespuesta,
    ServicioRespuesta,
)

# Esta configuracion cambia el titulo, la descripcion y la documentacion
# automatica que FastAPI genera en /docs y /redoc.
app = FastAPI(
    title="API TotalPlay",
    description="API REST para administrar clientes, servicios contratados, reportes y paquetes de TotalPlay.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Herwin Daniel Velazquez Abrego",
        "email": "herwinitech@gmail.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Datos en memoria: no usamos base de datos, se pierden al reiniciar el servidor.
clientes = []
consumos = []
paquetes = {
    "basico": 400.00,
    "intermedio": 500.00,
    "premium": 600.00,
}


# El middleware se ejecuta en todas las peticiones, antes y despues del endpoint.
@app.middleware("http")
async def validar_y_medir_tiempo(request: Request, call_next):
    inicio = time.perf_counter()

    # Validacion: si una peticion POST o PUT trae datos, deben venir en formato JSON.
    if request.method in ["POST", "PUT"]:
        trae_datos = request.headers.get("content-length", "0") != "0"
        tipo_contenido = request.headers.get("content-type", "")
        if trae_datos and "application/json" not in tipo_contenido:
            return JSONResponse(
                status_code=415,
                content={"detail": "Los datos deben enviarse en formato JSON"},
            )

    response = await call_next(request)
    tiempo = time.perf_counter() - inicio
    response.headers["X-Tiempo-Procesamiento"] = f"{tiempo:.4f}s"
    return response


# ---------------------------------------------------------------------------
# Reglas de negocio: funciones que reutilizamos en varios endpoints.
# ---------------------------------------------------------------------------

def buscar_cliente(id_cliente: int) -> ClienteRespuesta:
    for cliente in clientes:
        if cliente.id_cliente == id_cliente:
            return cliente
    raise HTTPException(status_code=404, detail="Cliente no encontrado")


def buscar_servicio(id_servicio: int) -> ServicioRespuesta:
    for servicio in consumos:
        if servicio.id_servicio == id_servicio:
            return servicio
    raise HTTPException(status_code=404, detail="Servicio no encontrado")


def validar_cliente_activo(cliente: ClienteRespuesta):
    if not cliente.active:
        raise HTTPException(
            status_code=400,
            detail="El cliente esta inactivo, no se pueden registrar ni actualizar sus servicios",
        )


def validar_fecha(fecha: date):
    if fecha > date.today():
        raise HTTPException(status_code=400, detail="La fecha de registro no puede ser futura")


# ---------------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------------

@app.get(
    "/v1/api/clientes",
    summary="Consultar todos los clientes",
    description="Devuelve la lista completa de clientes, activos e inactivos.",
    response_description="Lista de clientes",
    response_model=ListaClientesRespuesta,
    tags=["Clientes"],
    operation_id="consultarClientes",
)
def consultar_clientes() -> ListaClientesRespuesta:
    return ListaClientesRespuesta(
        success=True,
        total=len(clientes),
        clientes=clientes,
    )


@app.get(
    "/v1/api/clientes/{id_cliente}",
    summary="Consultar un cliente",
    description="Devuelve la informacion de un cliente por su identificador.",
    response_description="Cliente encontrado",
    response_model=ClienteOperacionRespuesta,
    tags=["Clientes"],
    operation_id="consultarCliente",
)
def consultar_cliente(
    id_cliente: int = Path(..., ge=1, description="Identificador del cliente"),
) -> ClienteOperacionRespuesta:
    cliente = buscar_cliente(id_cliente)
    return ClienteOperacionRespuesta(
        success=True,
        mensaje="Cliente encontrado",
        cliente=cliente,
    )


@app.post(
    "/v1/api/clientes",
    summary="Registrar un cliente",
    description="Registra un nuevo cliente. Todo cliente nuevo inicia activo.",
    response_description="Cliente registrado correctamente",
    response_model=ClienteOperacionRespuesta,
    status_code=201,
    tags=["Clientes"],
    operation_id="registrarCliente",
)
def registrar_cliente(datos: ClienteCrear) -> ClienteOperacionRespuesta:
    # Como nunca borramos clientes, el siguiente id es el tamano de la lista + 1.
    cliente = ClienteRespuesta(
        id_cliente=len(clientes) + 1,
        nombre_cliente=datos.nombre_cliente,
        direccion=datos.direccion,
        active=True,
    )
    clientes.append(cliente)
    return ClienteOperacionRespuesta(
        success=True,
        mensaje="Cliente registrado correctamente",
        cliente=cliente,
    )


@app.put(
    "/v1/api/clientes/{id_cliente}",
    summary="Actualizar un cliente",
    description="Actualiza el nombre y la direccion de un cliente.",
    response_description="Cliente actualizado correctamente",
    response_model=ClienteOperacionRespuesta,
    tags=["Clientes"],
    operation_id="actualizarCliente",
)
def actualizar_cliente(
    id_cliente: int = Path(..., ge=1, description="Identificador del cliente"),
    datos: ClienteActualizar = ...,
) -> ClienteOperacionRespuesta:
    cliente = buscar_cliente(id_cliente)
    cliente.nombre_cliente = datos.nombre_cliente
    cliente.direccion = datos.direccion
    return ClienteOperacionRespuesta(
        success=True,
        mensaje="Cliente actualizado correctamente",
        cliente=cliente,
    )


@app.delete(
    "/v1/api/clientes/{id_cliente}",
    summary="Desactivar un cliente",
    description="No borra al cliente: cambia active a false y el registro se conserva.",
    response_description="Cliente desactivado correctamente",
    response_model=ClienteOperacionRespuesta,
    tags=["Clientes"],
    operation_id="desactivarCliente",
)
def desactivar_cliente(
    id_cliente: int = Path(..., ge=1, description="Identificador del cliente"),
) -> ClienteOperacionRespuesta:
    cliente = buscar_cliente(id_cliente)
    if not cliente.active:
        raise HTTPException(status_code=400, detail="El cliente ya estaba inactivo")
    cliente.active = False
    return ClienteOperacionRespuesta(
        success=True,
        mensaje="Cliente desactivado correctamente",
        cliente=cliente,
    )


# ---------------------------------------------------------------------------
# Servicios contratados
# ---------------------------------------------------------------------------

@app.get(
    "/v1/api/servicios",
    summary="Consultar los servicios",
    description="Devuelve los servicios registrados. Se puede filtrar por cliente.",
    response_description="Lista de servicios",
    response_model=ListaServiciosRespuesta,
    tags=["Servicios"],
    operation_id="consultarServicios",
)
def consultar_servicios(
    id_cliente: Optional[int] = Query(
        default=None,
        ge=1,
        description="Opcional: solo los servicios de este cliente",
    ),
) -> ListaServiciosRespuesta:
    servicios = consumos
    if id_cliente is not None:
        servicios = [servicio for servicio in consumos if servicio.id_cliente == id_cliente]
    return ListaServiciosRespuesta(
        success=True,
        total=len(servicios),
        servicios=servicios,
    )


@app.post(
    "/v1/api/servicios",
    summary="Registrar un servicio",
    description="Registra el paquete que contrata un cliente activo.",
    response_description="Servicio registrado correctamente",
    response_model=ServicioOperacionRespuesta,
    status_code=201,
    tags=["Servicios"],
    operation_id="registrarServicio",
)
def registrar_servicio(datos: ServicioCrear) -> ServicioOperacionRespuesta:
    cliente = buscar_cliente(datos.id_cliente)
    validar_cliente_activo(cliente)

    # Si no mandan la fecha, se usa la de hoy.
    fecha = datos.fecha_registro
    if fecha is None:
        fecha = date.today()
    validar_fecha(fecha)

    servicio = ServicioRespuesta(
        id_servicio=len(consumos) + 1,
        id_cliente=cliente.id_cliente,
        paquete=datos.paquete,
        fecha_registro=fecha,
    )
    consumos.append(servicio)
    return ServicioOperacionRespuesta(
        success=True,
        mensaje="Servicio registrado correctamente",
        servicio=servicio,
    )


@app.put(
    "/v1/api/servicios/{id_servicio}",
    summary="Actualizar un servicio",
    description="Cambia el paquete (y opcionalmente la fecha) de un servicio de un cliente activo.",
    response_description="Servicio actualizado correctamente",
    response_model=ServicioOperacionRespuesta,
    tags=["Servicios"],
    operation_id="actualizarServicio",
)
def actualizar_servicio(
    id_servicio: int = Path(..., ge=1, description="Identificador del servicio"),
    datos: ServicioActualizar = ...,
) -> ServicioOperacionRespuesta:
    servicio = buscar_servicio(id_servicio)
    cliente = buscar_cliente(servicio.id_cliente)
    validar_cliente_activo(cliente)

    if datos.fecha_registro is not None:
        validar_fecha(datos.fecha_registro)
        servicio.fecha_registro = datos.fecha_registro
    servicio.paquete = datos.paquete
    return ServicioOperacionRespuesta(
        success=True,
        mensaje="Servicio actualizado correctamente",
        servicio=servicio,
    )


# ---------------------------------------------------------------------------
# Reporte
# ---------------------------------------------------------------------------

@app.get(
    "/v1/api/reportes/servicios",
    summary="Reporte de servicios",
    description="Servicios de clientes activos con el costo de su paquete. Se puede filtrar por fecha.",
    response_description="Reporte de servicios",
    response_model=ReporteRespuesta,
    tags=["Reportes"],
    operation_id="reporteServicios",
)
def reporte_servicios(
    fecha_inicio: Optional[date] = Query(
        default=None,
        description="Desde esta fecha (AAAA-MM-DD)",
    ),
    fecha_fin: Optional[date] = Query(
        default=None,
        description="Hasta esta fecha (AAAA-MM-DD)",
    ),
) -> ReporteRespuesta:
    if fecha_inicio is not None and fecha_fin is not None and fecha_inicio > fecha_fin:
        raise HTTPException(status_code=400, detail="La fecha de inicio no puede ser mayor que la fecha final")

    registros = []
    for servicio in consumos:
        cliente = buscar_cliente(servicio.id_cliente)

        # El reporte solo muestra clientes activos y servicios dentro del rango de fechas.
        if not cliente.active:
            continue
        if fecha_inicio is not None and servicio.fecha_registro < fecha_inicio:
            continue
        if fecha_fin is not None and servicio.fecha_registro > fecha_fin:
            continue

        registro = RegistroReporte(
            id_servicio=servicio.id_servicio,
            paquete=servicio.paquete,
            fecha_registro=servicio.fecha_registro,
            costo_paquete=paquetes[servicio.paquete],  # el costo se toma del precio actual
            cliente=ClienteReporte(
                id_cliente=cliente.id_cliente,
                nombre_cliente=cliente.nombre_cliente,
                direccion=cliente.direccion,
            ),
        )
        registros.append(registro)

    total_ingresos = 0
    for registro in registros:
        total_ingresos = total_ingresos + registro.costo_paquete

    return ReporteRespuesta(
        success=True,
        total=len(registros),
        total_ingresos=total_ingresos,
        registros=registros,
    )


# ---------------------------------------------------------------------------
# Paquetes
# ---------------------------------------------------------------------------

@app.get(
    "/v1/api/paquetes",
    summary="Consultar los paquetes",
    description="Devuelve los paquetes disponibles y su costo actual.",
    response_description="Paquetes y costos",
    response_model=ListaPaquetesRespuesta,
    tags=["Paquetes"],
    operation_id="consultarPaquetes",
)
def consultar_paquetes() -> ListaPaquetesRespuesta:
    return ListaPaquetesRespuesta(
        success=True,
        paquetes=paquetes,
    )


@app.put(
    "/v1/api/paquetes/{paquete}",
    summary="Actualizar el costo de un paquete",
    description="Cambia el costo de un paquete. Los calculos posteriores usan el nuevo costo.",
    response_description="Costo actualizado correctamente",
    response_model=PaqueteRespuesta,
    tags=["Paquetes"],
    operation_id="actualizarCostoPaquete",
)
def actualizar_costo_paquete(
    paquete: str = Path(..., description="basico, intermedio o premium"),
    datos: PaqueteActualizar = ...,
) -> PaqueteRespuesta:
    paquete = paquete.lower()
    if paquete not in paquetes:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    paquetes[paquete] = datos.costo
    return PaqueteRespuesta(
        success=True,
        mensaje="Costo actualizado correctamente",
        paquete=paquete,
        costo=datos.costo,
    )
