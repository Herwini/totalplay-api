"""
Capa de datos (lo que en clase llamamos "repository").

Aquí vive toda la información de la API. No usamos base de datos:
los datos se guardan en listas y diccionarios de Python, en memoria.
Si se reinicia el servidor, la información se pierde (es lo esperado
en esta actividad).
"""

# Cada cliente es un diccionario:
# {"id_cliente": 1, "nombre_cliente": "...", "direccion": "...", "active": True}
clientes = []

# Cada servicio contratado (consumo) es un diccionario:
# {"id_servicio": 1, "id_cliente": 1, "paquete": "basico", "fecha_registro": date}
consumos = []

# Paquetes disponibles y su costo actual.
# Si se actualiza un costo, los cálculos posteriores usan el nuevo valor.
paquetes = {
    "basico": 400.00,
    "intermedio": 500.00,
    "premium": 600.00,
}


def buscar_cliente(id_cliente: int):
    """Regresa el cliente con ese id, o None si no existe."""
    for cliente in clientes:
        if cliente["id_cliente"] == id_cliente:
            return cliente
    return None


def buscar_servicio(id_servicio: int):
    """Regresa el servicio con ese id, o None si no existe."""
    for servicio in consumos:
        if servicio["id_servicio"] == id_servicio:
            return servicio
    return None


def siguiente_id(lista: list) -> int:
    """
    Genera el id del siguiente registro.
    Como nunca borramos registros físicamente (solo desactivamos),
    la lista nunca se hace más chica y el id nunca se repite.
    """
    return len(lista) + 1
