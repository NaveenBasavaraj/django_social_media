# Django Internals for This Project (Interview Depth)

This document explains only what exists in this repository today and how it works internally.
It intentionally does not cover features that are not yet implemented in this codebase.

## 0) 2026-03-10 Bug Fix: Migration Failure and Root Cause

Observed failure while running migrations:

- `uv run manage.py migrate` failed with `django.db.utils.ProgrammingError: relation "core_user_user" does not exist`.

Root cause:

- The project uses a custom user model (`AUTH_USER_MODEL = "core_user.User"`), but the app had no initial migration file.
- Because there was no `core_user.0001_initial`, Django could not build the `core_user_user` table before migrations that depend on the auth/user setup.

Fix applied:

1. Generated the missing migration with `uv run manage.py makemigrations core_user`.
2. Applied migrations with `uv run manage.py migrate`.
3. Fixed additional user-model bugs and generated a second migration:

- Added missing `is_staff` field required for proper admin/staff behavior.
- Corrected timestamp semantics to `created=auto_now_add` and `updated=auto_now`.
- Fixed `get_object_by_public_id` to raise `Http404` instead of returning it.

4. Applied the follow-up migration and verified with `uv run manage.py check`.

Current state:

- Migrations apply successfully.
- Django system checks report no issues.

## 1) Current Architecture Snapshot

Current top-level pieces:

- Project package: config
- Main command entrypoint: manage.py
- Apps registered: core, core.user, core.auth
- API stack installed: Django REST Framework + django-filter + markdown
- Database backend configured: PostgreSQL via psycopg2

What is implemented right now:

- Django project wiring (settings, ASGI, WSGI, root URLconf)
- Custom user model class in core.user.models
- Custom user manager methods for create_user/create_superuser and public id lookup

What is not implemented yet:

- App-level URL routing (no include(...) in root URLconf)
- View logic for user/auth (files are scaffolded but empty)
- Serializers (core.user.serializers is empty)
- App-level API features (views/serializers/routes) are still scaffold-level

This is important in interviews: knowing what is configured vs what is only scaffolded shows real depth.

## 2) MVC vs Django MVT (and how to explain this project)

Interview framing:

- Classic pattern: MVC (Model-View-Controller)
- Django pattern: MVT (Model-View-Template)

Mapping between them:

- Model (MVC) == Model (Django): database entities and business rules
- View (MVC UI layer) ~= Template (Django): HTML presentation layer
- Controller (MVC) ~= Django View + URL dispatcher + middleware pipeline

For this project today:

- Model layer: partially present (custom User model)
- Controller-like flow: present at framework level (URL resolver + middleware + view dispatch pipeline)
- Template/UI layer: not used yet (no templates/custom HTML pages implemented)

Deeper level (request lifecycle):

1. Request enters ASGI/WSGI application object from config.asgi/config.wsgi.
2. Django builds HttpRequest and applies middleware chain.
3. URL resolver checks ROOT_URLCONF (config.urls).
4. Matching path maps to view callable/class.
5. View returns response, middleware post-processes it.
6. Response is returned to server/client.

In this repository, step 4 currently has only one route: admin/.

## 3) How Django Figures Out Project Name and App Names

### 3.1 Project package name (config)

Django knows the active project settings module from DJANGO_SETTINGS_MODULE.
In this repo it is set in three places to config.settings:

- manage.py
- config/asgi.py
- config/wsgi.py

Meaning:

- manage.py commands use config.settings
- ASGI server boot uses config.settings
- WSGI server boot uses config.settings

If this value is wrong, startup fails with import errors for settings.

### 3.2 App discovery and app identity

Django loads apps from INSTALLED_APPS in config.settings.
Current entries include:

- core
- core.user
- core.auth

How Django treats them internally:

- Each entry becomes an AppConfig instance.
- AppConfig.name is the full Python import path.
- AppConfig.label is the internal app registry key (must be unique).

In this repository:

- core.user has label core_user
- core.auth has label core_auth

Why labels matter:

- They avoid collisions when two apps might otherwise have same label.
- They are used in migration metadata and app registry internals.

## 4) URL Resolution in This Project

Current root URLconf (config.urls):

- admin/ -> django admin site

Depth 1: ROOT_URLCONF

- Setting ROOT_URLCONF = config.urls tells Django where the root urlpatterns live.

Depth 2: Resolver graph

- Django builds URLResolver and URLPattern objects from urlpatterns.
- Incoming path is matched left-to-right.

Depth 3: include(...) and namespacing (not yet used here)

- Normally large projects delegate by include('app.urls').
- This is not wired yet in this repo, so app-level routes do not exist.

Interview-quality statement for this repo:

- URL routing is currently single-node (admin only).
- Modular URL composition through include(...) is the next logical step but is not implemented yet.

## 5) PostgreSQL Connection: Detailed Flow

Configuration source:

- config/settings.py reads DB fields using python-decouple config(...).

Configured database dict:

- ENGINE: django.db.backends.postgresql_psycopg2
- NAME: DB_NAME
- USER: DB_USER
- PASSWORD: DB_PASSWORD
- HOST: DB_HOST
- PORT: DB_PORT

Depth 1: settings loading

- At startup, settings import executes.
- decouple reads environment values (typically from .env or OS env vars).

Depth 2: backend selection

- ENGINE selects Django PostgreSQL backend implementation.
- psycopg2-binary provides the PostgreSQL driver that actually opens sockets and executes SQL.

Depth 3: runtime usage

- Django ORM asks connection router for default DB.
- Backend constructs connection parameters.
- Connection is opened lazily (first DB operation), not always immediately at process start.
- Queries are executed via Django cursor wrappers around psycopg2 cursor/connection objects.

Migrations implication in this repo:

- Custom user migrations are now present and applied.
- The migration graph is consistent with `AUTH_USER_MODEL = "core_user.User"`.

## 6) Custom User Model: What It Inherits and What It Means

Class definition:

- User(AbstractBaseUser, PermissionsMixin)

### 6.1 AbstractBaseUser gives

- password hash field and password API (set_password/check_password)
- last_login field behavior
- authentication-related base behavior

### 6.2 PermissionsMixin gives

- is_superuser behavior
- groups and user_permissions M2M relations
- permission helper methods (has_perm, etc.)

### 6.3 Fields currently defined

- public_id: UUIDField, unique, indexed, non-editable, default uuid4
- username: unique/indexed
- first_name, last_name
- email: unique/indexed
- is_active
- is_superuser
- created, updated

Important note:

- created uses auto_now=True and updated uses auto_now_add=True in current code.
- Conventional intent is usually the reverse (created=auto_now_add, updated=auto_now).
- In interviews, mention this as current behavior, not intention.

### 6.4 USERNAME_FIELD and REQUIRED_FIELDS (how Django uses both)

Current code sets:

- USERNAME_FIELD = "email"
- REQUIRED_FIELDS = ["username"]

What USERNAME_FIELD does:

- It tells Django which model field is the unique login identifier.
- Management commands such as createsuperuser treat this as the primary credential prompt.
- The authentication backend and admin user creation flow depend on this constant.

What REQUIRED_FIELDS does:

- It lists extra fields that createsuperuser must ask for, in addition to USERNAME_FIELD and password.
- It does not force validation for normal create() calls by itself.
- It is mainly used by Django's superuser creation command and custom user model checks.

Interview-level rule:

- USERNAME_FIELD should point to one unique, stable identifier field.
- REQUIRED_FIELDS should include mandatory profile fields needed at superuser creation time.
- REQUIRED_FIELDS must not repeat USERNAME_FIELD.

In this project's current setup:

- Login identifier is email.
- createsuperuser should prompt for email + username + password.

### 6.5 Required settings linkage

This project correctly sets:

- AUTH_USER_MODEL = "core_user.User" (using app label + model class)

This ensures Django auth/admin references the custom `User` model.

## 7) UserManager Internals

Manager class: UserManager(BaseUserManager)

### 7.0 What a manager is, and why custom managers exist

In Django, a manager is the model's query and object-construction interface.

- Every model gets a default manager (objects) if not overridden.
- Manager methods run at class level, for example User.objects.filter(...).
- Managers centralize reusable query logic and creation policies.

Why use a custom manager for a custom user model:

- To enforce required fields consistently in create_user/create_superuser.
- To normalize credentials (for example normalize_email).
- To ensure passwords are hashed (set_password) before save.
- To provide domain-specific lookup methods such as get_object_by_public_id.

How this project wires the custom manager:

1. Define UserManager(BaseUserManager).
2. Implement creation and lookup methods.
3. Attach it on the model with objects = UserManager().

After this, calls like User.objects.create_user(...) use your custom manager implementation.

Implemented methods:

- get_object_by_public_id(public_id)
- create_user(username, email, password=None, \*\*kwargs)
- create_superuser(username, email, password, \*\*kwargs)

### 7.1 create_user

Flow:

1. Validate username/email/password are not None.
2. Normalize email via BaseUserManager.normalize_email.
3. Instantiate model.
4. Hash password using set_password.
5. Save with using=self.\_db.

Interview point:

- set_password is essential; assigning raw password directly is a security bug.

### 7.2 create_superuser

Flow:

1. Validate required fields.
2. Reuse create_user(...).
3. Set is_superuser and is_staff True.
4. Save.

Previous issue in this repository (now fixed):

- User model did not declare `is_staff` while `create_superuser` set `user.is_staff = True`.
- This has been fixed by adding a concrete `is_staff` model field and migrating.

### 7.3 get_object_by_public_id

Current behavior:

- Tries self.get(public_id=public_id)
- On ObjectDoesNotExist, ValueError, TypeError returns Http404 class

Key interview-level observation:

- It returns Http404 instead of raising Http404.
- Returning Http404 (class/object) is not normal flow for retrieval helper methods.
- Typical patterns are either:
  - raise Http404
  - return None
  - let DoesNotExist propagate

Also, user request mentioned get_objectby public id.
In this code the method name is get_object_by_public_id.

## 8) How manage.py, ASGI, WSGI, and settings connect

### 8.1 manage.py

- Sets DJANGO_SETTINGS_MODULE to config.settings
- Calls execute_from_command_line(sys.argv)
- This powers makemigrations, migrate, runserver, createsuperuser, etc.

### 8.2 asgi.py / wsgi.py

- Both set DJANGO_SETTINGS_MODULE to config.settings
- Build application callable via get_asgi_application/get_wsgi_application

Depth chain:

- Deployment server imports application callable
- Callable loads settings and app registry
- App registry initializes INSTALLED_APPS
- URL resolver uses ROOT_URLCONF

## 9) What has been done so far (project-reality summary)

Implemented:

- Project package rename to config and references updated
- PostgreSQL DB settings wired through decouple variables
- DRF-related packages installed and added
- core, core.user, core.auth apps registered
- Custom User model and manager written

Not yet implemented (but scaffold files exist):

- serializer classes
- API views/endpoints for auth or user
- app URL files and include wiring
- app-level business endpoints and request/response flows

This boundary is crucial for interviews: explain current state precisely, then explain next engineering steps only when asked.

## 10) Interview-ready one-minute explanation for this repo

"This project uses Django with a project package named config and modular apps under core. Startup entrypoints manage.py, asgi.py, and wsgi.py all resolve the same settings module, config.settings. The app registry is built from INSTALLED_APPS, where core.user and core.auth are explicitly configured with custom AppConfig labels. Routing is currently root-level with only the admin route, so URL dispatch pipeline exists but app endpoint composition is not yet wired.

Database connectivity is PostgreSQL using Django backend plus psycopg2-binary, and credentials are externalized through python-decouple. A custom User model exists based on AbstractBaseUser and PermissionsMixin with a UUID public_id and a custom manager for user creation and lookup by public_id. `AUTH_USER_MODEL` is wired, custom-user migrations are applied, and key model correctness issues (`is_staff`, timestamp fields, and Http404 handling) have been fixed."
