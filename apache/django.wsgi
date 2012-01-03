import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'ubsna.settings'

path = 'C:/Program Files/Apache Software Foundation/Apache2.2/django'
if path not in sys.path:
    sys.path.append(path)
    
import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()