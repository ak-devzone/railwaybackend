"""
Django settings for library_system project.
"""

from pathlib import Path
import os
import json
import tempfile
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
import pymysql

# Patch MySQL driver and fake version to satisfy Django 4.2+ requirement
pymysql.version_info = (2, 2, 1, 'final', 0)
pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / '.env')



# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-your-secret-key-here-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') + [
    'evelia-umbrose-unmovingly.ngrok-free.dev', '.vercel.app', '.vercel.pub', '.railway.app', 'localhost', '127.0.0.1'
]

# Configure Django to recognize HTTPS behind a proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

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
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files in production
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

# Database (MySQL via Railway)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'railway'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}
print(f"DEBUG: settings.py loaded. DB_HOST={DATABASES['default']['HOST']} DB_NAME={DATABASES['default']['NAME']}")

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
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Media files (Database Storage)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # Keep for fallback or static tools

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
CORS_ALLOWED_ORIGINS = [
    os.getenv('FRONTEND_URL', 'https://library-systemm.web.app'),
    'https://library-systemm.web.app',
    'https://library-systemm.firebaseapp.com',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    "https://evelia-umbrose-unmovingly.ngrok-free.dev",
]

CORS_ALLOW_ALL_ORIGINS = True

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    "https://evelia-umbrose-unmovingly.ngrok-free.dev",
    'https://*.railway.app',
    'https://*.up.railway.app',
    'https://library-systemm.web.app',
]

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
try:
    if not firebase_admin._apps:  # Check if not already initialized
        # Priority 1: JSON string from environment variable (Railway deployment)
        firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
        if firebase_creds_json:
            creds_dict = json.loads(firebase_creds_json)
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred, {
                'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', 'library-system.appspot.com')
            })
            print("Firebase Admin SDK initialized from FIREBASE_CREDENTIALS_JSON env var")
        else:
            # Priority 2: File path (local development)
            default_creds_path = os.path.join(BASE_DIR, 'firebase-credentials.json')
            parent_creds_path = os.path.join(BASE_DIR.parent, 'firebase-credentials.json')
            firebase_creds_path = os.getenv('FIREBASE_CREDENTIALS_PATH')

            if not firebase_creds_path:
                if os.path.exists(default_creds_path):
                    firebase_creds_path = default_creds_path
                elif os.path.exists(parent_creds_path):
                    firebase_creds_path = parent_creds_path

            if firebase_creds_path and os.path.exists(firebase_creds_path):
                cred = credentials.Certificate(firebase_creds_path)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', 'library-system.appspot.com')
                })
                print(f"Firebase Admin SDK initialized from file: {firebase_creds_path}")
            else:
                print("Warning: Firebase credentials not found. Set FIREBASE_CREDENTIALS_JSON env var for production.")
    else:
        print("Firebase Admin SDK already initialized")
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
# Use SSL for port 465, TLS for others (usually 587)
if EMAIL_PORT == 465:
    EMAIL_USE_TLS = False
    EMAIL_USE_SSL = True
else:
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Digital Library <noreplydigitallibrarysystemm@gmail.com>')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@digitallibrary.com')

# Prevent infinite hangs on SMTP calls (10 seconds)
EMAIL_TIMEOUT = 10

# Tracking deployment version
BUILD_VERSION = os.getenv('RAILWAY_GIT_COMMIT_SHA', 'local-dev')[:7]

# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_ENABLE_UTC = False
