from pydantic import BaseModel, Field
from datetime import date
from typing import Literal, Optional


class ClienteCrear(BaseModel):
   nombre: str = Field(...,max_length=100, min_length=3, description="Nombre del cliente")
   direccion: str = Field(...,max_length=200, min_length=3, description="Direccion del cliente")

class ServicioCrear(BaseModel):
   id_cliente: int = Field(..., ge=1, description="Id del cliente que contrata")
   paquete: Literal["basico", "intermedio", "premium"] = Field(..., description="basico, intermedio o premium")
   fecha_registro: Optional[date] = Field(default=None, description="AAAA-MM-DD. Si no se envia, se usa la fecha de hoy")

class ServicioActualizar(BaseModel):
   paquete: Literal["basico", "intermedio", "premium"] = Field(..., description="Nuevo paquete")
   fecha_registro: Optional[date] = Field(default=None, description="Si no se envia, se conserva la anteriorior")

class PaqueteActualizar(BaseModel):
    costo: float = Field(..., gt=0, description="Nuevo costo, mayor a 0")