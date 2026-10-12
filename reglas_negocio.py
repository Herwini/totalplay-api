"""
Reglas de negocio (lo que en clase llamamos "services").

Son funciones que se reutilizan en varios endpoints para no copiar
y pegar el mismo código. Si una regla cambia, solo se modifica aquí.

Códigos HTTP que usamos:
- 404: lo que se busca no existe (cliente, servicio o paquete).
- 400: la petición viene bien escrita, pero rompe una regla del negocio.
- 422: lo genera Pydantic solo, cuando los datos no tienen el formato correcto.
"""

from datetime import date
from typing import Optional

from fastapi import HTTPException

from datos import buscar_cliente, buscar_servicio, paquetes


def obtener_cliente_o_404(id_cliente: int) -> dict:
    """Busca el cliente; si no existe, detiene la petición con un 404."""
    cliente = buscar_cliente(id_cliente)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


def obtener_servicio_o_404(id_servicio: int) -> dict:
    """Busca el servicio; si no existe, detiene la petición con un 404."""
    servicio = buscar_servicio(id_servicio)
    if servicio is None:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return servicio


def validar_cliente_activo(cliente: dict) -> None:
    """Regla: solo se registran o actualizan servicios de clientes activos."""
    if not cliente["active"]:
        raise HTTPException(
            status_code=400,
            detail="El cliente está inactivo; no se pueden registrar ni actualizar sus servicios",
        )


def validar_fecha_no_futura(fecha: date) -> None:
    """Regla: un servicio no se puede registrar con una fecha que todavía no llega."""
    if fecha > date.today():
        raise HTTPException(status_code=400, detail="La fecha de registro no puede ser futura")


def validar_rango_fechas(fecha_inicio: Optional[date], fecha_fin: Optional[date]) -> None:
    """Regla: en el reporte, la fecha de inicio no puede ser mayor que la final."""
    if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
        raise HTTPException(
            status_code=400,
            detail="La fecha de inicio no puede ser mayor que la fecha final",
        )


def validar_paquete_existe(paquete: str) -> None:
    """Regla: solo se pueden modificar los paquetes que ofrece TotalPlay."""
    if paquete not in paquetes:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")


def calcular_costo(paquete: str) -> float:
    """El costo siempre se toma del diccionario, así usa el precio más reciente."""
    return paquetes[paquete]
