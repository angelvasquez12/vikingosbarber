"""
Formularios del sistema VikingCard.

Se usan `django.forms` (módulo interno de Django, pero externo a la lógica
propia de la vista) para centralizar la validación de datos de entrada de
los formularios administrativos del caso: inicio de sesión, registro de
clientes y recarga de saldo. Esto responde al indicador 1.1.2
("Determina las operaciones de entrada/salida y validaciones de datos
requeridas para procesar la lógica de los formularios administrativos").
"""
from django import forms

from . import data


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"placeholder": "tu@correo.com", "autofocus": True}),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••"}),
    )
    recordar = forms.BooleanField(
        label="Mantener mi sesión iniciada en este dispositivo",
        required=False,
    )


class RegistroForm(forms.Form):
    nombre = forms.CharField(
        label="Nombre",
        max_length=60,
        widget=forms.TextInput(attrs={"placeholder": "Kristian"}),
    )
    apellido = forms.CharField(
        label="Apellido",
        max_length=60,
        widget=forms.TextInput(attrs={"placeholder": "Soto"}),
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"placeholder": "tu@correo.com"}),
    )
    telefono = forms.CharField(
        label="Teléfono",
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "+56 9 1234 5678"}),
    )
    password = forms.CharField(
        label="Contraseña",
        min_length=8,
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••"}),
        help_text="Mínimo 8 caracteres.",
    )
    password_confirm = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••"}),
    )
    terminos = forms.BooleanField(
        label="Acepto los términos de uso de VikingCard y el tratamiento de mis datos personales.",
        required=True,
        error_messages={"required": "Debes aceptar los términos para crear tu VikingCard."},
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if data.existe_usuario(email):
            raise forms.ValidationError("Ya existe una cuenta VikingCard con este correo.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Las contraseñas no coinciden.")
        return cleaned_data


class RecargaForm(forms.Form):
    METODOS = [
        ("tarjeta", "Tarjeta de débito o crédito"),
        ("transferencia", "Transferencia bancaria"),
        ("efectivo", "Efectivo en sucursal"),
    ]

    monto = forms.IntegerField(
        label="Monto a recargar",
        min_value=data.RECARGA_MINIMA,
        widget=forms.NumberInput(attrs={"id": "monto", "step": 500}),
        error_messages={
            "min_value": f"El monto mínimo de recarga es ${data.RECARGA_MINIMA:,}".replace(",", "."),
        },
    )
    metodo = forms.ChoiceField(
        label="Método de pago",
        choices=METODOS,
        widget=forms.RadioSelect,
    )
