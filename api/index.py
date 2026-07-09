import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "luxe_project.settings")

import django
from django.conf import settings
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application


django.setup()

if (
    os.environ.get("VERCEL_ENV")
    or os.environ.get("VERCEL_URL")
    or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
):
    db_name = str(settings.DATABASES["default"]["NAME"])
    db_dir = str(Path(db_name).parent)
    if db_dir and db_dir != ".":
        os.makedirs(db_dir, exist_ok=True)
    call_command("migrate", interactive=False, verbosity=0)


application = get_wsgi_application()
app = application
