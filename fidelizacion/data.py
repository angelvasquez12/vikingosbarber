"""
Capa de datos "mock" del caso Tarjetas y Fidelización (VikingCard).

Requerimiento de la Evaluación 1 (Unidad 1): el sistema todavía NO se conecta
a una base de datos. Toda la información se carga desde archivos .json
(carpeta `fidelizacion/mock_data/`) hacia estructuras de datos en Python
(listas y diccionarios), tal como pide la pauta para la Fase 3
("Datos mock: Utilización de archivos .json o estructuras de datos en
Python... para simular temporalmente la información del sistema").

Como no hay persistencia real, los "usuarios registrados" viven en la lista
`USUARIOS` en memoria durante la ejecución del servidor: alcanza para
demostrar el flujo completo (registro -> login -> recarga -> transacciones)
dentro de una misma sesión de trabajo, y se reinicia cuando se reinicia el
servidor de desarrollo. La Unidad 2 reemplazará esta capa por modelos y
consultas reales a la base de datos.
"""
import json
import random
from datetime import date
from pathlib import Path

from django.contrib.auth.hashers import check_password, make_password

MOCK_DIR = Path(__file__).resolve().parent / "mock_data"

PUNTOS_POR_PESO = 1 / 1000  # 1 punto por cada $1.000 pagado con la tarjeta
RECARGA_MINIMA = 2000


def _cargar_json(nombre_archivo):
    """Lee un archivo .json de la carpeta mock_data y devuelve listas/diccionarios."""
    ruta = MOCK_DIR / nombre_archivo
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


# Estructuras "de solo lectura" (catálogo del sistema).
NIVELES = _cargar_json("niveles.json")
SERVICIOS = _cargar_json("servicios.json")
SUCURSALES = _cargar_json("sucursales.json")

# "Base de datos" en memoria de cuentas de clientes. Se inicializa con el
# usuario demo y va creciendo con cada registro nuevo mientras el servidor
# esté corriendo.
USUARIOS = _cargar_json("usuarios.json")


# ---------------------------------------------------------------------------
# Utilidades de dominio: niveles / fidelización
# ---------------------------------------------------------------------------
def calcular_nivel(puntos):
    """
    Determina el nivel actual de un cliente y su progreso hacia el siguiente,
    según los rangos de puntos definidos en NIVELES.

    Devuelve un diccionario listo para usar en el contexto de las plantillas:
    nombre del nivel actual, descuento, siguiente nivel, puntos que faltan
    y porcentaje de avance de la barra de progreso.
    """
    nivel_actual = NIVELES[0]
    for nivel in NIVELES:
        if puntos >= nivel["puntos_min"]:
            nivel_actual = nivel

    indice_actual = NIVELES.index(nivel_actual)
    siguiente_nivel = NIVELES[indice_actual + 1] if indice_actual + 1 < len(NIVELES) else None

    if siguiente_nivel:
        rango = siguiente_nivel["puntos_min"] - nivel_actual["puntos_min"]
        avance = puntos - nivel_actual["puntos_min"]
        progreso_pct = max(0, min(100, round((avance / rango) * 100)))
        puntos_faltantes = max(0, siguiente_nivel["puntos_min"] - puntos)
    else:
        progreso_pct = 100
        puntos_faltantes = 0

    return {
        "actual": nivel_actual,
        "siguiente": siguiente_nivel,
        "progreso_pct": progreso_pct,
        "puntos_faltantes": puntos_faltantes,
    }


def calcular_puntos_por_pago(monto):
    """1 punto por cada $1.000 pagados con la VikingCard."""
    return int(monto * PUNTOS_POR_PESO)


# ---------------------------------------------------------------------------
# Acceso a usuarios (simulando operaciones CRUD sin base de datos)
# ---------------------------------------------------------------------------
def obtener_usuario(email):
    """Busca un usuario por correo (case-insensitive). Devuelve None si no existe."""
    if not email:
        return None
    email_normalizado = email.strip().lower()
    for usuario in USUARIOS:
        if usuario["email"].lower() == email_normalizado:
            return usuario
    return None


def existe_usuario(email):
    return obtener_usuario(email) is not None


def autenticar(email, password):
    """Verifica credenciales contra la lista en memoria usando hash seguro."""
    usuario = obtener_usuario(email)
    if usuario is None:
        return None
    if check_password(password, usuario["password_hash"]):
        return usuario
    return None


def _generar_numero_tarjeta():
    """Genera 4 dígitos únicos para simular los últimos números de la tarjeta virtual."""
    numeros_usados = {usuario["tarjeta_numero"] for usuario in USUARIOS}
    while True:
        numero = f"{random.randint(0, 9999):04d}"
        if numero not in numeros_usados:
            return numero


def crear_usuario(nombre, apellido, email, telefono, password):
    """
    Crea (en memoria) una nueva cuenta VikingCard con saldo y puntos en cero.
    Equivale al "Create" del CRUD que en la Unidad 2 pasará a la base de datos.
    """
    nuevo_usuario = {
        "email": email.strip().lower(),
        "password_hash": make_password(password),
        "nombre": nombre.strip(),
        "apellido": apellido.strip(),
        "telefono": telefono.strip(),
        "tarjeta_numero": _generar_numero_tarjeta(),
        "saldo": 0,
        "puntos": 0,
        "fecha_registro": date.today().isoformat(),
        "movimientos": [],
    }
    USUARIOS.append(nuevo_usuario)
    return nuevo_usuario


def recargar_saldo(usuario, monto, metodo):
    """
    Aumenta el saldo del usuario y registra el movimiento de recarga.
    Devuelve el movimiento creado para poder mostrar feedback inmediato.
    """
    metodos = {
        "tarjeta": "Recarga de saldo (tarjeta)",
        "transferencia": "Recarga de saldo (transferencia)",
        "efectivo": "Recarga de saldo (efectivo en sucursal)",
    }
    usuario["saldo"] += monto
    movimiento = {
        "fecha": date.today().isoformat(),
        "detalle": metodos.get(metodo, "Recarga de saldo"),
        "sucursal": None,
        "tipo": "recarga",
        "puntos": 0,
        "monto": monto,
        "estado": "recarga",
    }
    usuario["movimientos"].insert(0, movimiento)
    return movimiento


def obtener_movimientos(usuario, tipo=None, sucursal=None, desde=None):
    """
    Filtra el historial de movimientos del usuario según los parámetros
    recibidos desde el formulario de filtros de la vista de transacciones.
    """
    movimientos = usuario["movimientos"]

    if tipo:
        movimientos = [m for m in movimientos if m["tipo"] == tipo]

    if sucursal:
        movimientos = [
            m for m in movimientos
            if m["sucursal"] and m["sucursal"].lower() == sucursal.strip().lower()
        ]

    if desde:
        movimientos = [m for m in movimientos if m["fecha"] >= desde]

    return sorted(movimientos, key=lambda m: m["fecha"], reverse=True)


_MAPA_SUCURSALES = {sucursal["id"]: sucursal["nombre"] for sucursal in SUCURSALES}


def nombre_sucursal(sucursal_id):
    """Traduce el id de una sucursal (usado en filtros/URLs) a su nombre visible."""
    return _MAPA_SUCURSALES.get(sucursal_id)


ESTADOS = {
    "pagado": {"etiqueta": "Pagado", "clase_css": "badge-success"},
    "recarga": {"etiqueta": "Recarga", "clase_css": "badge-recarga"},
    "en_revision": {"etiqueta": "En revisión", "clase_css": "badge-pending"},
}


def enriquecer_movimiento(movimiento):
    """
    Agrega al diccionario del movimiento la información ya "lista para la
    vista": nombre de sucursal y etiqueta/clase del estado. Se hace en una
    copia para no mutar los datos originales guardados en memoria.
    """
    enriquecido = dict(movimiento)
    enriquecido["sucursal_nombre"] = nombre_sucursal(movimiento["sucursal"])
    enriquecido["estado_info"] = ESTADOS.get(
        movimiento["estado"], {"etiqueta": movimiento["estado"], "clase_css": ""}
    )
    return enriquecido
