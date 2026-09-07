"""
Pruebas básicas del sistema VikingCard.

No son parte obligatoria de la pauta de la Evaluación 1, pero sirven para
verificar rápidamente que la navegación pública, el control de acceso a las
páginas privadas y la lógica de niveles/recarga (sin base de datos) siguen
funcionando después de cualquier cambio.

Ejecutar con: python manage.py test
"""
from django.test import TestCase
from django.urls import reverse

from . import data

EMAIL_DEMO = "kristian@vikingosbarber.cl"
PASSWORD_DEMO = "vikingo123"


class PaginasPublicasTests(TestCase):
    def test_inicio_responde_200(self):
        respuesta = self.client.get(reverse("fidelizacion:inicio"))
        self.assertEqual(respuesta.status_code, 200)

    def test_servicios_lista_el_catalogo_mock(self):
        respuesta = self.client.get(reverse("fidelizacion:servicios"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.context["servicios"]), len(data.SERVICIOS))


class ControlDeAccesoTests(TestCase):
    def test_dashboard_redirige_a_login_sin_sesion(self):
        respuesta = self.client.get(reverse("fidelizacion:dashboard"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("fidelizacion:login"), respuesta.url)

    def test_login_valido_permite_entrar_al_dashboard(self):
        self.client.post(
            reverse("fidelizacion:login"),
            {"email": EMAIL_DEMO, "password": PASSWORD_DEMO},
        )
        respuesta = self.client.get(reverse("fidelizacion:dashboard"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Kristian")

    def test_login_invalido_muestra_error(self):
        respuesta = self.client.post(
            reverse("fidelizacion:login"),
            {"email": EMAIL_DEMO, "password": "clave-incorrecta"},
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Correo o contraseña incorrectos")


class CalculoDeNivelTests(TestCase):
    def test_nivel_guerrero_con_340_puntos(self):
        info = data.calcular_nivel(340)
        self.assertEqual(info["actual"]["id"], "guerrero")
        self.assertEqual(info["siguiente"]["id"], "berserker")
        self.assertEqual(info["progreso_pct"], 47)

    def test_nivel_maximo_sin_siguiente(self):
        info = data.calcular_nivel(5000)
        self.assertEqual(info["actual"]["id"], "jarl")
        self.assertIsNone(info["siguiente"])
        self.assertEqual(info["progreso_pct"], 100)


class RecargaSaldoTests(TestCase):
    def setUp(self):
        self.client.post(
            reverse("fidelizacion:login"),
            {"email": EMAIL_DEMO, "password": PASSWORD_DEMO},
        )

    def test_recarga_exitosa_actualiza_saldo(self):
        usuario_antes = data.obtener_usuario(EMAIL_DEMO)
        saldo_inicial = usuario_antes["saldo"]

        respuesta = self.client.post(
            reverse("fidelizacion:recargar"),
            {"monto": 5000, "metodo": "efectivo"},
        )

        self.assertEqual(respuesta.status_code, 302)
        usuario_despues = data.obtener_usuario(EMAIL_DEMO)
        self.assertEqual(usuario_despues["saldo"], saldo_inicial + 5000)

    def test_recarga_bajo_el_minimo_no_se_aplica(self):
        usuario_antes = data.obtener_usuario(EMAIL_DEMO)
        saldo_inicial = usuario_antes["saldo"]

        respuesta = self.client.post(
            reverse("fidelizacion:recargar"),
            {"monto": 100, "metodo": "efectivo"},
        )

        self.assertEqual(respuesta.status_code, 200)  # vuelve a mostrar el form con error
        usuario_despues = data.obtener_usuario(EMAIL_DEMO)
        self.assertEqual(usuario_despues["saldo"], saldo_inicial)
