from django.contrib import admin
from .models import Cliente, Tarjeta, Historial


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("run", "nombre", "apellido", "telefono", "correo", "estado")
    search_fields = ("run", "nombre", "apellido", "correo")
    list_filter = ("estado",)


@admin.register(Tarjeta)
class TarjetaAdmin(admin.ModelAdmin):
    list_display = ("codigo_tarjeta", "cliente", "sellos_acumulados", "sellos_meta", "estado")
    search_fields = ("codigo_tarjeta", "cliente__nombre", "cliente__run")
    list_filter = ("estado",)


@admin.register(Historial)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ("tarjeta", "tipo_movimiento", "descripcion", "monto_pagado", "fecha_hora")
    search_fields = ("tarjeta__codigo_tarjeta", "descripcion")
    list_filter = ("tipo_movimiento",)