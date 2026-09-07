"""
Rutas de la app 'fidelizacion' (VikingCard).

Se usa `path()` con nombres de ruta (`name=`) para poder referenciar cada
URL desde las plantillas mediante `{% url %}` en vez de escribir rutas
"a mano", evitando enlaces rotos si el prefijo cambia en el futuro.
"""
from django.urls import path

from . import views

app_name = "fidelizacion"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("servicios/", views.servicios, name="servicios"),

    path("cuenta/registro/", views.registro, name="registro"),
    path("cuenta/login/", views.iniciar_sesion, name="login"),
    path("cuenta/logout/", views.cerrar_sesion, name="logout"),

    path("cuenta/", views.dashboard, name="dashboard"),
    path("cuenta/recargar/", views.recargar, name="recargar"),
    path("cuenta/transacciones/", views.transacciones, name="transacciones"),
]
