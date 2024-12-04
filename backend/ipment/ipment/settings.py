import os
import base64
from pathlib import Path
from decouple import config, Csv
from dotenv import load_dotenv

def decode_base64(value):
    return base64.b64decode(value).decode('utf-8')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!


SECRET_KEY = config('SECRET_KEY', default='')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', cast=Csv())


# Application definition

INSTALLED_APPS = [
    'apps.UserAccount.apps.UserAccountConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'apps.ActivityLog.apps.ActivityLogConfig',  
    'apps.iPM.apps.iPMConfig',
    'apps.Configuration.apps.ConfigurationConfig',
]

CORS_ORIGIN_ALLOW_ALL = config('CORS_ORIGIN_ALLOW_ALL', default=True, cast=bool) # True = Enable all domaind to access all the APIs, not recommended in production
CORS_ALLOW_CREDENTIALS = config('CORS_ALLOW_CREDENTIALS', default=True, cast=bool)
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())
CORS_ALLOW_METHODS = config('CORS_ALLOW_METHODS', cast=Csv())
CORS_ALLOW_HEADERS = config('CORS_ALLOW_HEADERS', cast=Csv())

# Security settings. Prevent cookies from being send to any external requests.
CSRF_COOKIE_SAMESITE = config('CSRF_COOKIE_SAMESITE', default='Strict')
SESSION_COOKIE_SAMESITE = config('SESSION_COOKIE_SAMESITE', default='Strict')

CSRF_COOKIE_HTTPONLY = config('CSRF_COOKIE_HTTPONLY', default=True, cast=bool) # False = Don't need to access csrf cookies from frontend. For production, set to True.
SESSION_COOKIE_HTTPONLY = config('SESSION_COOKIE_HTTPONLY', default=True, cast=bool) # True = To access session cookies from frontend

CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default='True')
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default='True')

# Enable HSTS. Ensure clients use HTTPS.
# SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default='31536000')  # 1 year, recommended value
# SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True, cast=bool)  # Apply HSTS to all subdomains
# SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=True, cast=bool)  # Allow your site to be included in the HSTS preload list

#Ensure that the site is only accessible via HTTPS
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)  # Redirect all HTTP requests to HTTPS

# Implement X-Content-Type-Options. Prevent browsers from interpreting files as a different MIME type.
SECURE_CONTENT_TYPE_NOSNIFF = config('SECURE_CONTENT_TYPE_NOSNIFF', default=True, cast=bool)

#Protect against clickjacking attacks.
X_FRAME_OPTIONS = config('SECURE_BROWSER_XSS_FILTER', default='DENY')

#Enable the browser's built-in XSS filter.
SECURE_BROWSER_XSS_FILTER = config('SECURE_BROWSER_XSS_FILTER', default=True, cast=bool)

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ipment.urls'

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

WSGI_APPLICATION = 'ipment.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': decode_base64(config('MYSQL_DATABASE', default='Y2ljdA==')), # cict
        'USER': decode_base64(config('MYSQL_USER', default='cm9vdA==')), # root
        'PASSWORD': decode_base64(config('MYSQL_PASSWORD', default='')),
        'HOST': decode_base64(config('MYSQL_HOST', default='bG9jYWxob3N0')), # localhost (or your database host)
        # 'PORT': config('MYSQL_PORT', default='3306'), # No need to specify if using the default port
    },
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


LOGIN_URL = "/UserAccount/login/"

# LOGIN_REDIRECT_URL = None

# LOGOUT_REDIRECT_URL = "/UserAccount/login/"

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'