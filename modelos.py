from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------------

# Modelo usado para devolver informacion de un cliente desde la API.
# Tambien es la forma en que guardamos cada cliente en la lista.
class ClienteRespuesta(BaseModel):
    id_cliente: int
    nombre_cliente: str
    direccion: str
    active: bool


# Modelo para los datos que recibimos al registrar un cliente.
class ClienteCrear(BaseModel):
    nombre_cliente: str = Field(
        min_length=3,
        max_length=100,
        description="Nombre completo del cliente",
        examples=["Juan Perez Lopez"],
    )
    direccion: str = Field(
        min_length=5,
        max_length=200,
        description="Direccion donde se instala el servicio",
        examples=["Av. Constitucion 123, Monterrey, N.L."],
    )


# En una actualizacion completa, los dos campos son obligatorios.
class ClienteActualizar(BaseModel):
    nombre_cliente: str = Field(
        min_length=3,
        max_length=100,
        description="Nuevo nombre del cliente",
        examples=["Juan Perez Garza"],
    )
    direccion: str = Field(
        min_length=5,
        max_length=200,
        description="Nueva direccion del cliente",
        examples=["Av. Constitucion 500, Monterrey, N.L."],
    )


# Respuesta al consultar todos los clientes.
class ListaClientesRespuesta(BaseModel):
    success: bool
    total: int
    clientes: list[ClienteRespuesta]


# Respuesta al consultar, registrar, actualizar o desactivar un cliente.
class ClienteOperacionRespuesta(BaseModel):
    success: bool
    mensaje: str
    cliente: ClienteRespuesta


# ---------------------------------------------------------------------------
# Servicios contratados
# ---------------------------------------------------------------------------

# Modelo usado para devolver informacion de un servicio desde la API.
# Tambien es la forma en que guardamos cada servicio en la lista.
class ServicioRespuesta(BaseModel):
    id_servicio: int
    id_cliente: int
    paquete: str
    fecha_registro: date


# Modelo para los datos que recibimos al registrar un servicio.
class ServicioCrear(BaseModel):
    id_cliente: int = Field(
        ge=1,
        description="Identificador del cliente que contrata",
        examples=[1],
    )
    # Literal: solo acepta uno de estos tres textos, cualquier otro da error 422.
    paquete: Literal["basico", "intermedio", "premium"] = Field(
        description="Paquete contratado: basico, intermedio o premium",
        examples=["basico"],
    )
    fecha_registro: Optional[date] = Field(
        default=None,
        description="Fecha AAAA-MM-DD. Si no se envia, se usa la fecha de hoy",
        examples=["2026-10-12"],
    )


# Modelo para los datos que recibimos al actualizar un servicio.
class ServicioActualizar(BaseModel):
    paquete: Literal["basico", "intermedio", "premium"] = Field(
        description="Nuevo paquete: basico, intermedio o premium",
        examples=["premium"],
    )
    fecha_registro: Optional[date] = Field(
        default=None,
        description="Fecha AAAA-MM-DD. Si no se envia, se conserva la anterior",
        examples=["2026-10-12"],
    )


# Respuesta al consultar los servicios.
class ListaServiciosRespuesta(BaseModel):
    success: bool
    total: int
    servicios: list[ServicioRespuesta]


# Respuesta al registrar o actualizar un servicio.
class ServicioOperacionRespuesta(BaseModel):
    success: bool
    mensaje: str
    servicio: ServicioRespuesta


# ---------------------------------------------------------------------------
# Reporte
# ---------------------------------------------------------------------------

# Datos del cliente que aparecen dentro de cada registro del reporte.
class ClienteReporte(BaseModel):
    id_cliente: int
    nombre_cliente: str
    direccion: str


# Un renglon del reporte.
class RegistroReporte(BaseModel):
    id_servicio: int
    paquete: str
    fecha_registro: date
    costo_paquete: float
    cliente: ClienteReporte


# Respuesta completa del reporte.
class ReporteRespuesta(BaseModel):
    success: bool
    total: int
    total_ingresos: float
    registros: list[RegistroReporte]


# ---------------------------------------------------------------------------
# Paquetes
# ---------------------------------------------------------------------------

# Modelo para el nuevo costo de un paquete.
class PaqueteActualizar(BaseModel):
    costo: float = Field(
        gt=0,
        description="Nuevo costo del paquete, debe ser mayor a 0",
        examples=[650.00],
    )


# Respuesta al consultar los paquetes.
class ListaPaquetesRespuesta(BaseModel):
    success: bool
    paquetes: dict[str, float]


# Respuesta al actualizar el costo de un paquete.
class PaqueteRespuesta(BaseModel):
    success: bool
    mensaje: str
    paquete: str
    costo: float
