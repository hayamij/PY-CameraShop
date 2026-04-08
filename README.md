# PY-CameraShop

E-commerce web application for cameras and accessories built with Flask and Clean Architecture, covering guest browsing, customer order flow, and admin operations.

## 1) About project

- Scope: authentication, catalog search/filter, cart management, checkout, order tracking, and admin management.
- Architecture: 4-layer clean separation (domain, business, adapters, infrastructure).
- Backend: Flask app factory with use-case wiring and repository adapters.
- Frontend: server-rendered templates plus static CSS/JS assets.

## 2) Tech stack

| Frontend | Backend API | Security | Database | Testing | Tooling |
|---|---|---|---|---|---|
| Jinja2 templates, HTML, CSS, vanilla JavaScript, Plotly (admin dashboard) | Python 3, Flask 3.0, SQLAlchemy 2, Flask-Migrate | Session-based auth, bcrypt password hashing | SQL Server (primary config), SQLite (testing/in-memory paths in scripts/config) | Pytest, pytest-flask | Docker, Alembic, Black, Flake8, Mypy |

## 3) Quick setup

- Prerequisites: Python 3.11+, pip, virtual environment, SQL Server (for default runtime).
- Install:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- Environment: create `.env` from `.env.example` and adjust DB/security settings.

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=mssql+pyodbc://sa:YourStrong@Password123@localhost:1433/CameraShopDB?driver=ODBC+Driver+17+for+SQL+Server
```

- Database init options:
  - SQL Server script: run `database-setup.sql` in SSMS.
  - Scripted SQL Server init: `python scripts/init_sqlserver.py`.
  - Docker init path is automated via `docker-compose.yml` + `scripts/init_sqlserver_docker.py`.

- Run:

```powershell
python app.py
pytest
```

- Default URL: `http://localhost:5000`

## 4) Docker quick start

```powershell
docker-compose up -d --build
```

- App: `http://localhost:5000`
- SQL Server container: `localhost:1433`

## 5) Architecture and patterns

- Clean architecture layout:
  - Domain: `app/domain`
  - Business: `app/business`
  - Adapters: `app/adapters`
  - Infrastructure: `app/infrastructure`
- Dependency direction: `Infrastructure -> Adapters -> Business -> Domain`.
- Core patterns: use-case orchestration, repository ports/adapters, application factory wiring, DTO-style input/output data classes in use-case modules.

## 6) Source inventory (snapshot)

Snapshot date: 2026-04-08

| Area | Files | Lines | Details |
|---|---:|---:|---|
| Python code volume | 166 | 35,603 | App package 91 / 12,799; Root app entry 1 / 12; Scripts 6 / 616; Migrations 2 / 211; Tests 66 / 21,965 |
| Repository footprint (tracked files) | 217 | 46,798 | requirements entries: 62 |
| Layer distribution (`app/`) | - | - | Domain 16 / 1,994; Business 43 / 5,769; Adapters 18 / 4,060; Infrastructure 13 / 969 |
| Domain/business components | - | - | Domain entities 6; Value objects 3; Use cases 33; Repository ports 6 |
| Adapter/infra components | - | - | API route files 6; View route files 1; Repository adapters 6; ORM model files 4 |
| UI assets | 35 | 9,734 | Templates 18 / 3,248; CSS 15 / 6,191; JS 2 / 295 |
| Database setup script | 1 | 325 | CREATE TABLE 9; CREATE INDEX 18; INSERT INTO 11 |

- API surface summary:
  - API endpoints: 35 (`GET 11`, `POST 11`, `PUT 7`, `DELETE 6`)
  - Frontend view routes: 15 (`GET 15`)
  - System routes in app factory: 2 (`/health`, `/`)
  - Total HTTP routes (API + view + system): 52

## 7) API groups

| Group | Base path | Endpoints |
|---|---|---:|
| Auth | `/api/auth` | 4 |
| Products | `/api/products` | 2 |
| Catalog | `/api/catalog` | 2 |
| Cart | `/api/cart` | 4 |
| Orders | `/api/orders` | 4 |
| Admin | `/api/admin` | 19 |
| View pages | `/`, `/products`, `/cart`, `/checkout`, `/orders`, `/admin/*` | 15 |

## 8) Testing and quality

- Test files: 66 Python test files.
- Discovered test functions (`def test_*`): 274.
- Test module distribution: adapters 2, api 8, business 35, domain 12, integration 7.
- Run tests:

```powershell
pytest
```

## 9) Demo credentials (seed)

- Credentials vary by initialization path/script in the repository.
- SQL seed (`database-setup.sql`) includes examples like:
  - Admin: `admin@gmail.com` / `123456`
  - Customer: `customer@gmail.com` / `123456`
- Script seed (`scripts/seed_data.py`) includes examples like:
  - Admin: `adminn` / `123123`
  - Customer: `john_doe` / `password123`

## 10) License

MIT License (see `LICENSE`).
