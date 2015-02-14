<<<<<<< HEAD
"""
WSGI config for _project410 project.
=======

"""
WSGI config for gettingstarted project.
>>>>>>> pro/master

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
<<<<<<< HEAD
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
=======
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
>>>>>>> pro/master
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_project410.settings")

from django.core.wsgi import get_wsgi_application
<<<<<<< HEAD
application = get_wsgi_application()
=======
from dj_static import Cling

application = Cling(get_wsgi_application())
>>>>>>> pro/master
