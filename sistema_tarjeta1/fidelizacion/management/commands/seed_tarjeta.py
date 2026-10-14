from django.core.management.base import BaseCommand
from fidelizacion.models import Cliente, Tarjeta
from faker import Faker


class Command(BaseCommand):
    help = "Genera TARJETA de prueba"

    def handle(self, *args, **kwargs):

        fake = Faker("es_CL")

        clientes = Cliente.objects.filter(tarjeta__isnull=True)

        for cliente in clientes:

            Tarjeta.objects.create(
                cliente=cliente,

                codigo_tarjeta = "TAR-" + fake.unique.numerify("########"),

                sellos_meta = 10,

                estado = cliente.estado
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Tarjetas creadas correctamente."
            )
        )