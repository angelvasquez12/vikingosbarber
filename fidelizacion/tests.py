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

class AdministracionClientesTests(TestCase):
    def setUp(self):
        self.client.post(
            reverse("fidelizacion:login"),
            {"email": EMAIL_DEMO, "password": PASSWORD_DEMO},
        )

    def test_lista_requiere_sesion(self):
        self.client.get(reverse("fidelizacion:logout"))
        respuesta = self.client.get(reverse("fidelizacion:usuarios"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("fidelizacion:login"), respuesta.url)

    def test_lista_muestra_clientes_y_stats(self):
        respuesta = self.client.get(reverse("fidelizacion:usuarios"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, EMAIL_DEMO)
        self.assertIn("stats", respuesta.context)

    def test_no_admin_es_redirigido_al_dashboard(self):
        data.crear_usuario(
            nombre="Sin",
            apellido="Permisos",
            email="sinpermisos@vikingosbarber.cl",
            telefono="+56900000000",
            password="sinpermisos123",
        )
        self.client.get(reverse("fidelizacion:logout"))
        self.client.post(
            reverse("fidelizacion:login"),
            {"email": "sinpermisos@vikingosbarber.cl", "password": "sinpermisos123"},
        )
        respuesta = self.client.get(reverse("fidelizacion:usuarios"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("fidelizacion:dashboard"), respuesta.url)
        data.eliminar_usuario("sinpermisos@vikingosbarber.cl")

    def test_crear_cliente(self):
        respuesta = self.client.post(
            reverse("fidelizacion:usuario_nuevo"),
            {
                "nombre": "Test",
                "apellido": "Admin",
                "email": "admintest@vikingosbarber.cl",
                "telefono": "+56911111111",
                "password": "admintest123",
            },
        )
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(data.existe_usuario("admintest@vikingosbarber.cl"))

    def test_editar_cliente(self):
        data.crear_usuario(
            nombre="Edit",
            apellido="Original",
            email="editartest@vikingosbarber.cl",
            telefono="+56922222222",
            password="editartest123",
        )
        respuesta = self.client.post(
            reverse("fidelizacion:usuario_editar", args=["editartest@vikingosbarber.cl"]),
            {"nombre": "Editado", "apellido": "Cambiado", "telefono": "+56933333333"},
        )
        self.assertEqual(respuesta.status_code, 302)
        usuario = data.obtener_usuario("editartest@vikingosbarber.cl")
        self.assertEqual(usuario["nombre"], "Editado")
        self.assertEqual(usuario["telefono"], "+56933333333")
        data.eliminar_usuario("editartest@vikingosbarber.cl")

    def test_eliminar_cliente(self):
        data.crear_usuario(
            nombre="Borrar",
            apellido="Test",
            email="borrartest@vikingosbarber.cl",
            telefono="+56944444444",
            password="borrartest123",
        )
        respuesta = self.client.post(
            reverse("fidelizacion:usuario_eliminar", args=["borrartest@vikingosbarber.cl"])
        )
        self.assertEqual(respuesta.status_code, 302)
        self.assertFalse(data.existe_usuario("borrartest@vikingosbarber.cl"))

    def test_no_se_puede_autoeliminar(self):
        respuesta = self.client.post(
            reverse("fidelizacion:usuario_eliminar", args=[EMAIL_DEMO])
        )
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(data.existe_usuario(EMAIL_DEMO))

    def test_buscador_filtra_por_nombre(self):
        respuesta = self.client.get(reverse("fidelizacion:usuarios") + "?q=kristian")
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, EMAIL_DEMO)
        respuesta = self.client.get(reverse("fidelizacion:usuarios") + "?q=nadieexiste123")
        self.assertNotContains(respuesta, EMAIL_DEMO)

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
