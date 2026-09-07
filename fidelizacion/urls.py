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

    path("administracion/usuarios/", views.usuarios_lista, name="usuarios"),
    path("administracion/usuarios/nuevo/", views.usuario_nuevo, name="usuario_nuevo"),
    path(
        "administracion/usuarios/<str:email>/editar/",
        views.usuario_editar,
        name="usuario_editar",
    ),
    path(
        "administracion/usuarios/<str:email>/eliminar/",
        views.usuario_eliminar,
        name="usuario_eliminar",
    ),
]
