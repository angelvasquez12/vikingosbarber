from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SEGURIDAD: el valor real vive en el archivo .env (no versionado en git).
# python-decouple permite mantener la SECRET_KEY y el modo DEBUG fuera del
# código fuente, siguiendo buenas prácticas de seguridad para el backend.
SECRET_KEY = config(
    'SECRET_KEY',
    default='django-insecure-=p+mf7ns(t5t!swv86&zb#)u25d3+_3uclvr*^n#*y^-2dy8od',
)

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='127.0.0.1,localhost',
    cast=lambda v: [host.strip() for host in v.split(',') if host.strip()],
)


# Application definition
#
# En esta fase no se incluyen 'django.contrib.admin', 'django.contrib.auth'
# ni 'django.contrib.contenttypes' porque requieren una base de datos
# migrada, y el requerimiento de la Evaluación 1 es NO conectar base de
# datos todavía (eso corresponde a la Unidad 2). La autenticación de
# usuarios se resuelve de forma manual en `fidelizacion.views` usando
# sesiones de Django sobre datos mock.

INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Paquete externo: agrega filtros/plantillas para enriquecer el
    # renderizado de formularios HTML manteniendo el diseño propio del sitio.
    'widget_tweaks',

    # App propia del caso "Tarjetas y Fidelización" (VikingCard).
    'fidelizacion',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'vikingcard.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'vikingcard.wsgi.application'


# Database
# ---------------------------------------------------------------------------
# Evaluación 1 (Unidad 1): sin conexión a base de datos. Se deja la
# configuración por defecto de Django lista para la Unidad 2, pero el
# proyecto nunca ejecuta `migrate` ni realiza consultas ORM en esta etapa.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Sesiones
# ---------------------------------------------------------------------------
# Al no usar base de datos, las sesiones se guardan firmadas directamente en
# la cookie del cliente en vez de en la tabla django_session.
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_AGE = 60 * 60 * 4  # 4 horas
SESSION_COOKIE_HTTPONLY = True


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'es-cl'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
