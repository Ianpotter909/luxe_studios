# Luxe Studio Django

Django booking website for Luxe Studio, configured for deployment on Vercel.

## Local setup

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Vercel

Set the Vercel project root to this `luxe_django` directory.

Required environment variable:

```text
SECRET_KEY=your-production-secret-key
```

Optional environment variables for a custom domain:

```text
DJANGO_ALLOWED_HOSTS=example.com,www.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
```
