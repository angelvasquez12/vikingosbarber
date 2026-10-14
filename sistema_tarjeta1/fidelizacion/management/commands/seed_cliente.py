from django.core.management.base import BaseCommand
from fidelizacion.models import Cliente
from faker import Faker
import random


def calcular_dv(numero):
    suma = 0
    multiplicador = 2

    for digito in reversed(str(numero)):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1

    resto = 11 - (suma % 11)

    if resto == 11:
        return "0"
    if resto == 10:
        return "K"
    return str(resto)


def generar_run(numero):
    return f"{numero}-{calcular_dv(numero)}"


class Command(BaseCommand):
    help = "Genera CLIENTE de prueba"

    def handle(self, *args, **kwargs):

        fake = Faker("es_CL")
        Cliente.objects.all().delete()

        for i in range(20):

            numero = fake.unique.random_int(
                min=5000000,
                max=25999999
            )

            Cliente.objects.create(
                run = generar_run(numero),

                nombre = fake.first_name_male(),

                apellido = fake.last_name(),

                telefono = fake.numerify(text="+569########"),

                correo = fake.unique.safe_email(),

                estado = random.choice([
                    True,
                    False
                ])
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Clientes creados correctamente."
            )
        )