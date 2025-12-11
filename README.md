# Expense Tracker (Django)

A minimal expense-tracking web app built with Django 4.x and Python 3.11.

## Features
- Dashboard with current month total, daily breakdown, and recent expenses
- Monthly view with total and full list
- Simple JSON API at `/api/expenses/`
- Admin to manage expenses

## Quickstart

### 1) Create and activate a virtual environment (Windows PowerShell)
```pwsh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies
```pwsh
pip install -r requirements.txt
```

### 3) Set up Django project
```pwsh
python manage.py migrate
python manage.py createsuperuser
```

### 4) Run the server
```pwsh
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` for the dashboard and `http://127.0.0.1:8000/admin/` for admin.

## Project Structure
```
expense_tracker/
  manage.py
  expense_tracker/
    settings.py
    urls.py
    wsgi.py
  expenses/
    models.py
    admin.py
    views.py
    urls.py
    forms.py
    templates/
      base.html
      dashboard.html
      monthly.html
    static/
  requirements.txt
  Procfile
  runtime.txt
  .gitignore
  README.md
```

## Deployment Notes
- `ALLOWED_HOSTS = ['*']` is set for quick deploy; change to your actual domain(s) in production.
- Uses SQLite by default for simplicity; switch to a managed database for production.
- Procfile runs: `web: gunicorn expense_tracker.wsgi`
- runtime.txt specifies `python-3.11`

### Deploy to Render (example)
1. Push to GitHub:
```pwsh
git init
git add .
git commit -m "Initial expense tracker"
# Create a GitHub repo first, then:
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```
2. On Render.com, create a new Web Service, connect your repo.
3. Set build command to `pip install -r requirements.txt`.
4. Set start command to `gunicorn expense_tracker.wsgi`.
5. Add environment variable `DJANGO_SECRET_KEY`.

## Notes
- Tailwind CSS is included via CDN in `base.html`.
- Static files are configured; for production, collect with `python manage.py collectstatic`.
- Change `TIME_ZONE` in settings if needed.