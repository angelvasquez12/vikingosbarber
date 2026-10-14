from django.core.management.base import BaseCommand
from fidelizacion.models import Tarjeta, Historial
from faker import Faker


class Command(BaseCommand):
    help = "Genera HISTORIAL de prueba"

    def handle(self, *args, **kwargs):

        fake = Faker("es_CL")

        servicios = {
            "Corte de pelo": 10000,
            "Corte + barba": 15000,
            "Perfilado de barba": 6000,
            "Afeitado clásico": 8000,
            "Corte infantil": 7000,
            "Diseño / degradado": 12000,
            "Lavado + peinado": 5000
        }

        premios = [
            "Corte de pelo gratis",
            "Perfilado de barba gratis",
            "Afeitado clásico gratis"
        ]

        for tarjeta in Tarjeta.objects.filter(estado=True):

            for i in range(fake.random_int(min=1, max=15)):

                servicio = fake.random_element(
                    elements=list(servicios.keys())
                )

                Historial.objects.create(
                    tarjeta=tarjeta,

                    tipo_movimiento = "Atención",

                    cantidad_sellos = 1,

                    descripcion=servicio,

                    monto_pagado = servicios[servicio]
                )

                tarjeta.sellos_acumulados += 1

                if tarjeta.sellos_acumulados >= tarjeta.sellos_meta:

                    Historial.objects.create(
                        tarjeta=tarjeta,

                        tipo_movimiento="Canje",

                        cantidad_sellos = tarjeta.sellos_meta,

                        descripcion = fake.random_element(
                            elements = premios
                        ),

                        monto_pagado = None
                    )

                    tarjeta.sellos_acumulados = 0

            tarjeta.save()

        self.stdout.write(
            self.style.SUCCESS(
                "Historial creado correctamente."
            )
        )