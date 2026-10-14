from django.db import models


class Cliente(models.Model):
    cliente_id = models.AutoField(primary_key=True)
    run = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField(unique=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Tarjeta(models.Model):
    id_tarjeta = models.AutoField(primary_key=True)
    cliente = models.OneToOneField(
        Cliente,
        on_delete=models.CASCADE,
        related_name="tarjeta"
    )
    codigo_tarjeta = models.CharField(max_length=50, unique=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    sellos_acumulados = models.PositiveIntegerField(default=0)
    sellos_meta = models.PositiveIntegerField(default=10)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"Tarjeta {self.codigo_tarjeta}"

class Historial(models.Model):
    id_historial = models.AutoField(primary_key=True)
    tarjeta = models.ForeignKey(
        Tarjeta,
        on_delete=models.CASCADE,
        related_name="historial"
    )
    fecha_hora = models.DateTimeField(auto_now_add=True)
    tipo_movimiento = models.CharField(max_length=30)
    cantidad_sellos = models.PositiveIntegerField(default=1)
    descripcion = models.TextField(blank=True, null=True)
    monto_pagado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.tarjeta.codigo_tarjeta}"
    
# python3 manage.py makemigrations
# python3 manage.py migrate