#
# Damit die Definition der DB-Einstellungen an einer Stelle erfolgt
#

import os

DATABASES = {
    'default': {
        'ENGINE'   : 'django.db.backends.postgresql',
        'NAME'     : os.environ.get('DBNAME', default='hilgi_wiesen'),
        'USER'     : os.environ.get('DBUSR', default='uws'),
        'PASSWORD' : os.environ.get('DBPWD', default='admin123'),
        'HOST'     : os.environ.get('DBHOST', default='localhost'),
        'PORT'     : os.environ.get('DBPORT', default='5432'),
    }
}
