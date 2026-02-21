"""
Django settings for library_system project.
"""

from pathlib import Path
import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / '.env')

# Monkeypatch to support MariaDB 10.4 (XAMPP default) with Django 5+
# Only applied when running against local XAMPP (not Railway)
import os as _os
_db_host = _os.getenv('DB_HOST', 'shortline.proxy.rlwy.net')
if 'localhost' in _db_host or '127.0.0.1' in _db_host:
    try:
        from django.db.backends.mysql.base import DatabaseWrapper
        DatabaseWrapper.check_database_version_supported = lambda self: None
        from django.db.backends.mysql.features import DatabaseFeatures
        DatabaseFeatures.can_return_columns_from_insert = False
    except ImportError:
        pass

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-your-secret-key-here-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') + [
    'evelia-umbrose-unmovingly.ngrok-free.dev', '.vercel.app', '.vercel.pub', '.railway.app', 'localhost', '127.0.0.1'
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Must be right after SecurityMiddleware
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'api.middleware.RemoveXFrameOptionsMiddleware',
    'api.middleware.FirebaseAuthenticationMiddleware',
]

ROOT_URLCONF = 'library_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'library_system.wsgi.application'

# Database
# - Set USE_SQLITE=True in .env for local development (no Railway needed)
# - Leave USE_SQLITE unset in production (Vercel) to use Railway MySQL
if os.getenv('USE_SQLITE', 'False') == 'True':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'railway'),
            'USER': os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'HmJtbgnUTrWRdfksUmvlwEKbkhKygomI'),
            'HOST': os.getenv('DB_HOST', 'shortline.proxy.rlwy.net'),
            'PORT': os.getenv('DB_PORT', '40877'),
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')
# Media files (Database Storage)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Keep for fallback or static tools

STORAGES = {
    "default": {
        "BACKEND": "api.storage.DatabaseStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# File upload size limits (must be > PDF limit of 25 MB for multipart form totals)
DATA_UPLOAD_MAX_MEMORY_SIZE = 30 * 1024 * 1024   # 30 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 30 * 1024 * 1024   # 30 MB

# CORS settings
_frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
_extra_vercel_frontend = os.getenv('VERCEL_FRONTEND_URL', '')

CORS_ALLOWED_ORIGINS = [
    _frontend_url,
    'http://127.0.0.1:3000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'https://evelia-umbrose-unmovingly.ngrok-free.dev',
] + ([_extra_vercel_frontend] if _extra_vercel_frontend else [])

CORS_ALLOW_ALL_ORIGINS = True  # Keep True for easy development; restrict in final production

CSRF_TRUSTED_ORIGINS = [
    _frontend_url,
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'https://evelia-umbrose-unmovingly.ngrok-free.dev',
    'https://*.vercel.app',
] + ([_extra_vercel_frontend] if _extra_vercel_frontend else [])

# Allow iframe embedding
X_FRAME_OPTIONS = 'ALLOWALL'

CORS_ALLOW_CREDENTIALS = True

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# Firebase Admin SDK initialization
# Supports three modes:
#   1. FIREBASE_CREDENTIALS_JSON  env var — JSON string (Vercel/production)
#   2. FIREBASE_CREDENTIALS_PATH  env var — path to .json file (local override)
#   3. Auto-detect firebase-credentials.json in backend/ or project root (local dev)
try:
    if not firebase_admin._apps:
        firebase_cred = None

        # Mode 1: Inline JSON string (preferred for Vercel)
        firebase_json_str = os.getenv('FIREBASE_CREDENTIALS_JSON')
        if firebase_json_str:
            firebase_cred_dict = json.loads(firebase_json_str)
            firebase_cred = credentials.Certificate(firebase_cred_dict)
            print("Firebase Admin SDK: using FIREBASE_CREDENTIALS_JSON env var")

        # Mode 2 & 3: File path
        if not firebase_cred:
            default_creds_path = os.path.join(BASE_DIR, 'firebase-credentials.json')
            parent_creds_path = os.path.join(BASE_DIR.parent, 'firebase-credentials.json')
            firebase_creds_path = os.getenv('FIREBASE_CREDENTIALS_PATH')

            if not firebase_creds_path:
                if os.path.exists(default_creds_path):
                    firebase_creds_path = default_creds_path
                elif os.path.exists(parent_creds_path):
                    firebase_creds_path = parent_creds_path

            if firebase_creds_path and os.path.exists(firebase_creds_path):
                firebase_cred = credentials.Certificate(firebase_creds_path)
                print(f"Firebase Admin SDK: using file {firebase_creds_path}")
            else:
                print("Warning: Firebase credentials not found — authentication will not work")

        if firebase_cred:
            firebase_admin.initialize_app(firebase_cred, {
                'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', 'library-system.appspot.com')
            })
            print("Firebase Admin SDK initialized successfully")
    else:
        print("Firebase Admin SDK already initialized")
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@digitallibrary.com')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@digitallibrary.com')

# Celery Configuration
# NOTE: Celery is NOT used on Vercel (serverless). These settings are for
# local development or if you run a separate worker on Railway/Render.
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_ENABLE_UTC = False
