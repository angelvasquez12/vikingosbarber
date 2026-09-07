"""
Vistas del sistema VikingCard (Vikingos Barber).

Cada función captura la petición, arma un diccionario de contexto con datos
mock (sin base de datos todavía) y lo renderiza hacia el template HTML
correspondiente, siguiendo la navegación definida en el diagrama de flujo
de la Fase 1: páginas públicas (inicio, servicios, login, registro) y
páginas de la app privada (dashboard, recargar, transacciones) que
requieren una sesión iniciada.
"""
from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from . import data
from .forms import LoginForm, RecargaForm, RegistroForm

SESSION_KEY = "usuario_email"


# ---------------------------------------------------------------------------
# Control de acceso a las páginas privadas (sin django.contrib.auth: se
# valida manualmente contra la sesión y los datos mock del usuario).
# ---------------------------------------------------------------------------
def requiere_sesion(vista):
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        email = request.session.get(SESSION_KEY)
        usuario = data.obtener_usuario(email) if email else None
        if usuario is None:
            messages.warning(request, "Debes iniciar sesión para continuar.")
            url_login = reverse("fidelizacion:login")
            return redirect(f"{url_login}?next={request.path}")
        request.usuario = usuario
        request.nivel_info = data.calcular_nivel(usuario["puntos"])
        return vista(request, *args, **kwargs)

    return envoltura


def _usuario_actual(request):
    email = request.session.get(SESSION_KEY)
    return data.obtener_usuario(email) if email else None


# ---------------------------------------------------------------------------
# Páginas públicas
# ---------------------------------------------------------------------------
def inicio(request):
    usuario = _usuario_actual(request)
    contexto = {
        "activo": "inicio",
        "niveles": data.NIVELES,
        "servicios_destacados": [s for s in data.SERVICIOS if s["id"] in (2, 3, 5)],
        "usuario": usuario,
        "nivel_info": data.calcular_nivel(usuario["puntos"]) if usuario else None,
    }
    return render(request, "index.html", contexto)


def servicios(request):
    contexto = {
        "activo": "servicios",
        "servicios": data.SERVICIOS,
        "usuario": _usuario_actual(request),
    }
    return render(request, "servicios.html", contexto)


def registro(request):
    if request.session.get(SESSION_KEY):
        return redirect("fidelizacion:dashboard")

    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            data.crear_usuario(
                nombre=datos["nombre"],
                apellido=datos["apellido"],
                email=datos["email"],
                telefono=datos["telefono"],
                password=datos["password"],
            )
            messages.success(
                request,
                "Tu VikingCard fue creada con éxito. Ya puedes iniciar sesión.",
            )
            return redirect("fidelizacion:login")
    else:
        form = RegistroForm()

    return render(request, "registro.html", {"form": form})


def iniciar_sesion(request):
    if request.session.get(SESSION_KEY):
        return redirect("fidelizacion:dashboard")

    siguiente = request.GET.get("next") or request.POST.get("next") or ""

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            usuario = data.autenticar(email, password)
            if usuario is not None:
                request.session[SESSION_KEY] = usuario["email"]
                if form.cleaned_data.get("recordar"):
                    request.session.set_expiry(60 * 60 * 24 * 14)  # 14 días
                else:
                    request.session.set_expiry(0)  # expira al cerrar el navegador
                messages.success(request, f"Bienvenido de vuelta, {usuario['nombre']}.")
                return redirect(siguiente or reverse("fidelizacion:dashboard"))
            form.add_error(None, "Correo o contraseña incorrectos.")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form, "next": siguiente})


def cerrar_sesion(request):
    request.session.flush()
    messages.info(request, "Cerraste sesión correctamente. ¡Hasta la próxima, guerrero!")
    return redirect("fidelizacion:inicio")


# ---------------------------------------------------------------------------
# Páginas privadas (requieren sesión iniciada)
# ---------------------------------------------------------------------------
@requiere_sesion
def dashboard(request):
    usuario = request.usuario
    movimientos_recientes = [
        data.enriquecer_movimiento(m)
        for m in data.obtener_movimientos(usuario)[:4]
    ]

    contexto = {
        "activo": "dashboard",
        "usuario": usuario,
        "nivel_info": request.nivel_info,
        "movimientos_recientes": movimientos_recientes,
    }
    return render(request, "dashboard.html", contexto)


@requiere_sesion
def recargar(request):
    usuario = request.usuario

    if request.method == "POST":
        form = RecargaForm(request.POST)
        if form.is_valid():
            monto = form.cleaned_data["monto"]
            metodo = form.cleaned_data["metodo"]
            data.recargar_saldo(usuario, monto, metodo)
            monto_formateado = f"${monto:,}".replace(",", ".")
            messages.success(request, f"Recargaste {monto_formateado} a tu VikingCard.")
            return redirect("fidelizacion:dashboard")
    else:
        form = RecargaForm(initial={"monto": 10000, "metodo": "tarjeta"})

    contexto = {
        "activo": "recargar",
        "usuario": usuario,
        "nivel_info": request.nivel_info,
        "form": form,
        "montos_rapidos": [10000, 20000, 30000, 50000],
        "monto_minimo": data.RECARGA_MINIMA,
    }
    return render(request, "recargar.html", contexto)


@requiere_sesion
def transacciones(request):
    usuario = request.usuario

    tipo = request.GET.get("tipo", "")
    sucursal = request.GET.get("sucursal", "")
    desde = request.GET.get("desde", "")

    movimientos = [
        data.enriquecer_movimiento(m)
        for m in data.obtener_movimientos(usuario, tipo=tipo, sucursal=sucursal, desde=desde)
    ]

    contexto = {
        "activo": "transacciones",
        "usuario": usuario,
        "nivel_info": request.nivel_info,
        "movimientos": movimientos,
        "sucursales": data.SUCURSALES,
        "filtros": {"tipo": tipo, "sucursal": sucursal, "desde": desde},
    }
    return render(request, "transacciones.html", contexto)
