
# SKY Health Check App

A team health check web application built with Django. Inspired by the Spotify Squad Health Check model, it lets engineering teams run regular voting sessions where members rate different aspects of team health (health cards) using a traffic-light system — **Green**, **Amber**, or **Red** — with optional comments and trend indicators. Results roll up into team, department, and organisation-level summaries for leaders and managers.

Built as a group project at the University of Westminster.

---

## Features

- **User accounts & profiles** — sign-up, login/logout, password change, and editable profiles with role, department, and team assignment
- **Role-based access** — supports Engineer, Team Leader, Department Leader, Senior Manager, and Admin roles
- **Chained dropdowns** — team selection is dynamically filtered by the chosen department (via `django-smart-selects`)
- **Health check voting wizard** — step-by-step wizard where users vote Green/Amber/Red on each health card for an active session, add comments, and mark trends
- **Sessions** — health checks are organised into time-boxed sessions linked to teams and projects
- **Summaries & dashboards** — personal summaries, team summaries, and a guide explaining how to read results
- **Static pages** — home, about, help, and contact pages
- **Admin panel** — manage projects, departments, teams, sessions, health cards, and votes through Django admin

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Django 6 |
| Database | PostgreSQL (production / Docker), SQLite (local default) |
| Frontend | Django templates, custom CSS |
| Forms / UI | django-smart-selects (chained dropdowns) |
| Server | Gunicorn + WhiteNoise (static files) |
| Config | dj-database-url (12-factor `DATABASE_URL`) |
| Deployment | Docker, Docker Compose, Railway, Render |

## Project Structure

```
.
├── accounts/            # Main app: models, views, templates, migrations
│   ├── models.py        # Project, Department, Team, Session, HealthCard, Profile, Votes
│   ├── views.py         # Auth, voting wizard, summaries, profile management
│   ├── urls.py          # App routes
│   └── templates/       # HTML templates (login, signup, wizard, summaries, etc.)
├── groupproject/        # Django project settings, root URLs, WSGI/ASGI
├── static/              # CSS and images
├── Dockerfile           # Production image (Gunicorn, collectstatic, migrations)
├── docker-compose.yml   # Local stack: web + PostgreSQL 16
├── railway.toml         # Railway deployment config
├── render.yaml          # Render deployment config
├── requirements.txt
└── manage.py
```

## Data Model

- **Project** → has many **Teams** and **Sessions**
- **Department** → has many **Teams**
- **Team** → belongs to a Department, optionally a Project
- **Session** → a time-boxed health check period for a Team
- **HealthCard** → a health topic being voted on (e.g. delivery, teamwork, codebase)
- **Profile** → extends the built-in Django `User` with full name, role, department, and team
- **Votes** → one user's Green/Amber/Red vote on a card in a session, with comment, trend, and submitted flag

## Getting Started

### Option 1 — Docker (recommended)

Requires Docker and Docker Compose.

```bash
git clone https://github.com/milandesilva/SKY-health-ckeck-App.git
cd SKY-health-ckeck-App
docker compose up --build
```

The app runs at http://localhost:8000 with a PostgreSQL 16 database. Migrations run automatically on startup.

To create an admin user:

```bash
docker compose exec web python manage.py createsuperuser
```

### Option 2 — Local (SQLite)

Requires Python 3.12+.

```bash
git clone https://github.com/milandesilva/SKY-health-ckeck-App.git
cd SKY-health-ckeck-App

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit http://127.0.0.1:8000/accounts/login/ to log in, or `/admin/` to seed departments, teams, sessions, and health cards.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key | — (required in production) |
| `DEBUG` | Debug mode | `False` in production |
| `ALLOWED_HOSTS` | Comma-separated hosts | — |
| `DATABASE_URL` | Database connection string | Local SQLite file |
| `CSRF_TRUSTED_ORIGINS` | Trusted origins for CSRF | — |

## Deployment

The repo ships ready for two platforms:

- **Railway** — uses `railway.toml` and the `Dockerfile`. Railway injects `$PORT`; the container runs migrations then starts Gunicorn. Health check path: `/accounts/login/`.
- **Render** — uses `render.yaml` to provision a free PostgreSQL database and a Docker web service.

For either platform, set `SECRET_KEY`, `ALLOWED_HOSTS`, and `DATABASE_URL` (usually auto-provided by the platform's managed Postgres).

## Key Routes

| Route | Purpose |
|---|---|
| `/accounts/signup/` · `/accounts/login/` | Registration and authentication |
| `/accounts/home/` | Dashboard |
| `/accounts/healthcheck/` | Health check landing / session picker |
| `/accounts/healthcheck/<session_id>/` | Voting wizard |
| `/accounts/summary/` | Personal results summary |
| `/accounts/yourprofile/team_summary/` | Team-level results |
| `/accounts/yourprofile/` | Profile view and edit |
| `/admin/` | Django admin |

## License

This project was developed for academic purposes at the University of Westminster. No license has been specified — contact the repository owner before reusing.
