"""
Modelos de Pydantic (lo que en clase llamamos "esquemas").

Definen la estructura de los datos que la API RECIBE en el body.
Si algo no cumple (falta un campo, tipo incorrecto, paquete que no
existe, fecha inválida, costo negativo...), FastAPI responde solo
con un error 422 antes de entrar a nuestra función.
"""

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field

# Solo se aceptan estos tres textos como paquete.
# Cualquier otro valor (por ejemplo "gold") da error 422.
PaqueteValido = Literal["basico", "intermedio", "premium"]


class ClienteEntrada(BaseModel):
    """Datos para registrar (POST) o actualizar (PUT) un cliente."""

    nombre_cliente: str = Field(
        ...,
        min_length=3,
        max_length=100,
        pattern=r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü .]+$",  # solo letras y espacios, sin números
        description="Nombre completo del cliente (solo letras)",
        examples=["Juan Pérez López"],
    )
    direccion: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Dirección donde se instala el servicio",
        examples=["Av. Constitución 123, Monterrey, N.L."],
    )


class ServicioCrear(BaseModel):
    """Datos para registrar el paquete que contrata un cliente."""

    id_cliente: int = Field(..., ge=1, description="Id del cliente que contrata", examples=[1])
    paquete: PaqueteValido = Field(..., description="basico, intermedio o premium", examples=["basico"])
    fecha_registro: Optional[date] = Field(
        default=None,
        description="Formato AAAA-MM-DD. Si no se envía, se usa la fecha de hoy",
        examples=["2026-10-12"],
    )


class ServicioActualizar(BaseModel):
    """Datos para cambiar el paquete de un servicio existente."""

    paquete: PaqueteValido = Field(..., description="basico, intermedio o premium", examples=["premium"])
    fecha_registro: Optional[date] = Field(
        default=None,
        description="Formato AAAA-MM-DD. Si no se envía, se conserva la fecha anterior",
        examples=["2026-10-12"],
    )


class PaqueteCosto(BaseModel):
    """Nuevo costo de un paquete."""

    costo: float = Field(..., gt=0, description="Nuevo costo del paquete (mayor a 0)", examples=[450.00])
