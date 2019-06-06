import dj_database_url
from decouple import config

from secret_share.settings import *

DEBUG = False

ALLOWED_HOSTS = (
    'localhost',
    '127.0.0.1',
    'secret-share-kodziek.herokuapp.com',
)

DATABASES['default'] = dj_database_url.config(default=config('DATABASE_URL'))
