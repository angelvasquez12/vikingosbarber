# Vikingos Barber — VikingCard

Sistema de **tarjeta digital y fidelización** para la barbería ficticia
Vikingos Barber. Proyecto del caso semestral de **Programación Backend (INACAP)**.

Los clientes crean su cuenta, reciben una **VikingCard** virtual con saldo y
puntos, recargan fondos, y revisan su historial. Cada $1.000 pagado suma
1 punto y permite subir de nivel: Escudero → Guerrero → Berserker → Jarl.

## Cómo ejecutarlo

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

Abrir http://127.0.0.1:8000/

**Cuenta demo:** `kristian@vikingosbarber.cl` / `vikingo123`

## Importante

- **Sin base de datos** (Evaluación 1): los datos son mock en
  `fidelizacion/mock_data/*.json` y viven en memoria hasta reiniciar el
  servidor. No se ejecuta `migrate`.
- Para verificar que todo funciona: `python manage.py test` (9 pruebas).

## Estructura

```
vikingcard/          Configuración Django (settings, urls)
fidelizacion/        App principal: views, forms, urls, datos mock, tests
templates/           Vistas HTML con herencia y etiquetas Django
static/              CSS, JS y logo oficial de la barbería
```

**Siguiente etapa (Unidad 2):** reemplazar los datos mock por modelos reales
con base de datos y panel de administración de Django.
