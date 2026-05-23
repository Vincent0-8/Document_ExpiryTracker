"""
DocuGuard ERP — settings.py (FINAL & LENGKAP)
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-ganti-ini-di-production-dengan-key-panjang-random-123'

DEBUG = True

ALLOWED_HOSTS = ['*']

# ─── INSTALLED APPS ─────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps kelompok
    'authentication',       # Julianto
    # 'documents_hrd',      # Jacky  (uncomment setelah merge)
    # 'documents_staff',    # Vincent (uncomment setelah merge)
    # 'activity_log',       # Damai  (uncomment setelah merge)
    # 'categories',         # Arsat  (uncomment setelah merge)
]

# ─── MIDDLEWARE ─────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # OTP Middleware (Julianto) — proteksi global semua route
    'authentication.middleware.OTPMiddleware',
]

ROOT_URLCONF = 'docuguard_erp.urls'

# ─── TEMPLATES ──────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Custom context processor (Julianto)
                'authentication.context_processors.auth_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'docuguard_erp.wsgi.application'

# ─── DATABASE ───────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ─── CUSTOM USER MODEL ──────────────────────────────────
AUTH_USER_MODEL = 'authentication.CustomUser'

# ─── LOGIN / LOGOUT ─────────────────────────────────────
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/auth/dashboard/'
LOGOUT_REDIRECT_URL = '/auth/login/'

# ─── SESSION ────────────────────────────────────────────
SESSION_COOKIE_AGE = 3600               # 1 jam
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
# SESSION_COOKIE_SECURE = True          # Aktifkan di production (HTTPS)

# ─── CSRF ───────────────────────────────────────────────
CSRF_COOKIE_HTTPONLY = False            # False agar JS bisa baca jika perlu
CSRF_COOKIE_SAMESITE = 'Lax'
# CSRF_COOKIE_SECURE = True             # Aktifkan di production

# ─── PASSWORD VALIDATION ────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── INTERNATIONALIZATION ───────────────────────────────
LANGUAGE_CODE = 'id'
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_TZ = True

# ─── STATIC & MEDIA ─────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── MESSAGES FRAMEWORK ─────────────────────────────────
from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {
    message_constants.DEBUG:   'secondary',
    message_constants.INFO:    'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR:   'danger',
}

# ─── LOGGING ────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} — {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'authentication': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# ─── SECURITY HEADERS ───────────────────────────────────
# Uncomment semua ini saat deploy ke PythonAnywhere
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# X_FRAME_OPTIONS = 'DENY'
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
