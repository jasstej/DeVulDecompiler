import hashlib
import os
from urllib.parse import urlparse
from pathlib import Path

from .base import *

_DB_PASS = os.getenv('DB_PASSWORD')
if not _DB_PASS:
    try:
        with open('/run/secrets/db_superuser_pass', 'r') as f:
            _DB_PASS = f.read().strip()
    except FileNotFoundError:
        _DB_PASS = ''


# Worker auth token: prefer explicit env (plain token or pre-hashed), else file secret
_WORKER_AUTH_TOKEN = os.getenv('WORKER_AUTH_TOKEN')
_WORKER_AUTH_TOKEN_HASH = os.getenv('WORKER_AUTH_TOKEN_HASH')
if _WORKER_AUTH_TOKEN_HASH:
    WORKER_AUTH_TOKEN_HASH = _WORKER_AUTH_TOKEN_HASH
elif _WORKER_AUTH_TOKEN:
    WORKER_AUTH_TOKEN_HASH = hashlib.sha256(_WORKER_AUTH_TOKEN.encode()).hexdigest()
else:
    try:
        with open('/run/secrets/worker_auth_token', 'rb') as f:
            WORKER_AUTH_TOKEN_HASH = hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        # As a last resort in dev, leave unset; is_request_from_worker will require DEBUG
        WORKER_AUTH_TOKEN_HASH = None

def _db_from_env():
    # Support DATABASE_URL (Render/Heroku style) or discrete DB_* vars
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        u = urlparse(db_url)
        # Handle postgres:// or postgresql://
        name = (u.path or '/postgres').lstrip('/') or 'postgres'
        user = u.username or 'postgres'
        password = u.password or _DB_PASS
        host = u.hostname or 'localhost'
        port = str(u.port or '5432')
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': name,
            'USER': user,
            'PASSWORD': password,
            'HOST': host,
            'PORT': port,
        }
    # Fallback to discrete vars
    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'postgres'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', _DB_PASS),
        'HOST': os.getenv('DB_HOST', 'database'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }

DATABASES = {
    'default': _db_from_env()
}

_MEMCACHED_HOST = os.getenv('MEMCACHED_HOST')
_MEMCACHED_PORT = os.getenv('MEMCACHED_PORT', '11211')
if _MEMCACHED_HOST:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
            'LOCATION': f'{_MEMCACHED_HOST}:{_MEMCACHED_PORT}',
        }
    }
else:
    # Fallback to local memory cache when memcached is not configured
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

DEFAULT_FILE_STORAGE = os.getenv('DJANGO_FILE_STORAGE', DEFAULT_FILE_STORAGE)
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')
AWS_IS_GZIPPED = True
GZIP_CONTENT_TYPES = [
    'text/css',
    'text/javascript',
    'application/javascript',
    'application/x-javascript',
    'image/svg',
    'application/octet-stream',
]

USING_S3 = AWS_S3_ENDPOINT_URL is not None

_s3_access_key_id_path = Path('/run/secrets/s3_access_key_id')
_s3_secret_access_key_path = Path('/run/secrets/s3_secret_access_key')

if _s3_access_key_id_path.exists() and _s3_secret_access_key_path.exists():
    AWS_QUERYSTRING_AUTH = True
    AWS_S3_ACCESS_KEY_ID = _s3_access_key_id_path.read_text()
    AWS_S3_SECRET_ACCESS_KEY = _s3_secret_access_key_path.read_text()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO' if DEBUG else 'ERROR',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO' if DEBUG else 'ERROR',
        },
    }
}
