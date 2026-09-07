"""
Filtros personalizados de plantilla para VikingCard.

Requerimiento de la Fase 3: "Renderizado dinámico... incluyendo estructuras
como {% for %}, {% if %} y filtros de texto y formato." Además de los
filtros propios de Django (`|upper`, `|slice`, etc.), se agregan dos
filtros de dominio para no repetir lógica de formato dentro del HTML:

- clp: formatea números como pesos chilenos ($12.000 / -$8.000).
- fecha_corta / fecha_larga: transforman las fechas ISO ("2026-09-02") que
  vienen de los datos mock en los formatos usados por el diseño.
"""
from datetime import datetime

from django import template

register = template.Library()

_MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def _parsear_fecha(valor):
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


@register.filter(name="clp")
def clp(valor):
    """Formatea un entero como monto en pesos chilenos: 12000 -> '$12.000'."""
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return valor

    signo = "-" if numero < 0 else ""
    miles = f"{abs(numero):,}".replace(",", ".")
    return f"{signo}${miles}"


@register.filter(name="fecha_corta")
def fecha_corta(valor):
    """'2026-09-02' -> '02-09-2026' (formato usado en la tabla de transacciones)."""
    fecha = _parsear_fecha(valor)
    return fecha.strftime("%d-%m-%Y") if fecha else valor


@register.filter(name="puntos")
def puntos(precio):
    """1 punto por cada $1.000: 12000 -> 12. Se usa para mostrar '+X pts' en el catálogo."""
    try:
        return int(precio) // 1000
    except (TypeError, ValueError):
        return 0


@register.filter(name="fecha_larga")
def fecha_larga(valor):
    """'2026-09-02' -> '2 de septiembre, 2026' (formato usado en el resumen)."""
    fecha = _parsear_fecha(valor)
    if not fecha:
        return valor
    return f"{fecha.day} de {_MESES[fecha.month - 1]}, {fecha.year}"
