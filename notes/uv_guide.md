# uv Guide for Django on Windows

## What is uv

uv is a fast Python package and project manager written in Rust.
It can replace common workflows that use pip, venv, and pip-tools.

For Django projects, uv helps you:

- create and manage virtual environments
- install and remove packages quickly
- lock dependencies for reproducible installs
- run Python and Django commands inside the project environment

In this project, dependency state is stored in:

- pyproject.toml
- uv.lock

## Install uv on Windows

### Option 1: PowerShell install script

Run this in PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then restart PowerShell and verify:

```powershell
uv --version
```

### Option 2: Install with pip (fallback)

```powershell
pip install uv
uv --version
```

## Create a Django project with uv

### 1) Create and enter a folder

```powershell
mkdir django_social_media
cd django_social_media
```

### 2) Initialize a uv project

```powershell
uv init
```

This creates a starting pyproject.toml.

### 3) Add Django

```powershell
uv add django
```

### 4) Start the Django project

```powershell
uv run django-admin startproject config .
```

This creates:

- manage.py
- config/ (settings, urls, wsgi, asgi)

## Create an app

From the project root (same level as manage.py):

```powershell
uv run python manage.py startapp user
```

You will get a new user/ app folder.

## Daily Django commands with uv

Use uv run so commands execute in the project environment.

### Run migrations

```powershell
uv run python manage.py makemigrations
uv run python manage.py migrate
```

### Create superuser

```powershell
uv run python manage.py createsuperuser
```

### Run dev server

```powershell
uv run python manage.py runserver
```

### Open Django shell

```powershell
uv run python manage.py shell
```

## Add and remove dependencies

### Add a package

```powershell
uv add djangorestframework
```

### Add a dev-only package

```powershell
uv add --dev pytest
```

### Remove a package

```powershell
uv remove djangorestframework
```

Each command updates pyproject.toml and uv.lock.

## How this avoids requirements.txt

Traditional workflow often uses requirements.txt. With uv, you can use:

- pyproject.toml for declared dependencies
- uv.lock for exact resolved versions

This gives repeatable installs without manually maintaining requirements.txt.

Typical workflow:

```powershell
uv add django
uv sync
```

On another machine:

```powershell
uv sync
```

uv reads pyproject.toml + uv.lock and installs the exact dependency set.

## Optional: export requirements.txt when needed

If a deployment platform requires requirements.txt, you can export one:

```powershell
uv export --format requirements-txt -o requirements.txt
```

Use this only for compatibility. Keep pyproject.toml and uv.lock as the source of truth.

## Recommended files to commit

Commit these files:

- pyproject.toml
- uv.lock

Do not commit:

- .venv/

## Quick command reference

```powershell
uv --version
uv init
uv add django
uv run django-admin startproject config .
uv run python manage.py startapp user
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py runserver
uv sync
```
