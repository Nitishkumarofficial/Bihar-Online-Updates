# Bihar-Online-Updates
Nitish Kumar Web deblopper of Bihar Online Updates

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DJANGO_SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
$env:DJANGO_DEBUG = "True"
python manage.py migrate
python manage.py runserver
```

The local SQLite database is `db.sqlite3`; it is ignored by Git and is not
changed by deployment setup.

## Deploy the Django site on Render

GitHub Pages serves static files only and cannot run Django, Python, templates,
database queries, or form handling. The repository-root `index.html` is a
static Pages notice; the working website is rendered by Django from
`newsportal/templates/newsportal/home.html`.

1. Create a persistent PostgreSQL database on Render (or use another
   PostgreSQL provider) and keep its connection URL private.
2. In Render, create a Blueprint from this repository. In the web service's
   Environment settings, set `DATABASE_URL` to the database's private/internal
   connection URL.
3. The Blueprint generates `DJANGO_SECRET_KEY` privately and sets production
   mode. Add any custom host to `DJANGO_ALLOWED_HOSTS` and its HTTPS origin to
   `DJANGO_CSRF_TRUSTED_ORIGINS`.
4. After deployment, open the Render service URL. Static assets are collected
   during the build and served by WhiteNoise; database migrations run at start.
5. If the existing SQLite database contains updates to keep, export and import
   that data into PostgreSQL before directing visitors to the new service.
   The deployment does not copy, delete, or overwrite `db.sqlite3`.

The Render start command is:

```sh
python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

Do not commit `.env` files, production secret keys, database URLs, or passwords.
