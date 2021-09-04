import os

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
load_dotenv(dotenv_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"config.settings.{os.environ.get('CONFIG')}")

application = get_wsgi_application()
