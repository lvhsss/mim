import os
import sys

path = '/home/fler432v/mim_djan'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mim_djan.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()