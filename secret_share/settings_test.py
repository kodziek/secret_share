import dj_database_url
from decouple import config

from secret_share.settings import *

DEBUG = False

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
}
