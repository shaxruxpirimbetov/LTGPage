<div align="center">

# LTGPage

**Publish an HTML page in seconds — write it yourself or let AI generate it from a short description.**

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/Django-REST%20Framework-092E20?logo=django&logoColor=white)
![Gemini](https://img.shields.io/badge/Google-Gemini-8E75B2?logo=googlegemini&logoColor=white)

</div>

---

## Overview

LTGPage is a small hosting service for single-file HTML pages. A user signs up, sends a title, a description and the page's HTML, and immediately gets a public link to share. A second mode, **AI pages**, takes a plain-language prompt ("a landing page for a coffee shop") and asks Google Gemini to produce a complete, self-contained HTML document.

The repository contains:

- a **Django REST Framework API** (users, pages, AI pages, JWT authentication);
- a **single-file frontend** (`frontend/index.html`, no build step) with a landing page, API documentation, sign-up / sign-in, and a dashboard to create, edit and view pages.

## Features

- **Publish in three steps:** register → get JWT tokens → `POST` your HTML → share `/api/page/view/<id>/`.
- **AI page generation** from a prompt using Google Gemini (`google-genai`); the result is stored as a regular page.
- **Public gallery:** anyone can list pages and filter them by author (`?user=<username>`).
- **Ownership rules:** only the author (or a superuser) can edit or delete their content.
- **JWT authentication** with refresh tokens (access 5 h, refresh 1 day).
- **Rate limiting:** 10 requests/min for anonymous clients, 100 requests/min for authenticated users.
- **Configurable CORS:** open in development, restricted to an allow-list in production.

## Repository layout

```
.
├── LTGPage/                Django project (settings, urls, wsgi/asgi)
├── apps/
│   ├── user/               Registration, user management, permissions
│   ├── page/               Pages submitted by users + public HTML view
│   └── aipage/             AI-generated pages
├── utils/
│   └── ai.py               Gemini client and the HTML-generation prompt
├── frontend/
│   └── index.html          Landing, docs and dashboard (single file)
├── manage.py
└── requirements.txt
```

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, Django, Django REST Framework |
| Auth | `djangorestframework-simplejwt` |
| AI | Google Gemini via `google-genai` |
| Database | PostgreSQL (or any URL supported by `dj-database-url`) |
| Config | `python-decouple`, `django-cors-headers` |
| Frontend | Plain HTML / CSS / JavaScript, no build step |

## Getting started

### Prerequisites

- Python 3.12+ (required by current Django)
- A database URL (PostgreSQL recommended; `sqlite:///db.sqlite3` works for local development)
- A [Gemini API key](https://aistudio.google.com/app/apikey)

### Installation

```bash
git clone https://github.com/shaxruxpirimbetov/LTGPage.git
cd LTGPage

python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://localhost:3000          # used when DEBUG is off
DATABASE_URL=sqlite:///db.sqlite3
GEMINI_API_KEY=your-gemini-key
```

> **Tip:** `DEBUG` is a boolean and defaults to `False`. In production leave it unset or set `DEBUG=False`.

### Run

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API is now at `http://127.0.0.1:8000/`. To use the frontend, open `frontend/index.html` in a browser or serve the folder with any static server.

> **Note:** the frontend reads the API address from the `API_BASE` constant near the bottom of `frontend/index.html`. Set it to `http://127.0.0.1:8000` to work against your local backend.

## Quick example

```bash
# 1. register
curl -X POST http://127.0.0.1:8000/api/user/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "a-strong-password"}'

# 2. get tokens
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "a-strong-password"}'

# 3. publish a page
curl -X POST http://127.0.0.1:8000/api/page/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Hello", "description": "My first page", "html": "<h1>Hello, world!</h1>"}'

# 4. open it in a browser: http://127.0.0.1:8000/api/page/view/<id>/
```

## API reference

Authenticate with `Authorization: Bearer <access_token>`. Lists are paginated (`?page=`, 20 items per page). Request bodies are JSON.

### Auth

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/token/` | Obtain access and refresh tokens (`username`, `password`) |
| `POST` | `/api/refresh/` | Refresh the access token (`refresh`) |

### Users — `/api/user/`

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/user/` | public | Register (`username`, `password`, optional `first_name`, `last_name`, `email`) |
| `GET` | `/api/user/` | authenticated | List users (`id`, `username`, `first_name`, `last_name`) |
| `GET` | `/api/user/<id>/` | authenticated | Retrieve a user (same public fields) |
| `PUT` / `PATCH` | `/api/user/<id>/` | the user themself or superuser | Update `first_name`, `last_name`, `email`, `password` (superusers can also set `is_active`) |
| `DELETE` | `/api/user/<id>/` | the user themself or superuser | Delete an account |

E-mail addresses and permission flags are never returned by the public endpoints, and they cannot be changed through the API.

### Pages — `/api/page/`

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/page/` | public | List pages (filter by author: `?user=<username>`) |
| `POST` | `/api/page/` | authenticated | Create a page (`title`, `description` 5–500 chars, `html`) |
| `GET` | `/api/page/<id>/` | public | Retrieve a page with its HTML source |
| `PUT` / `PATCH` | `/api/page/<id>/` | owner or superuser | Update a page |
| `GET` | `/api/page/view/<id>/` | public | **Render** the page as HTML — this is the link you share |

### AI pages — `/api/ai-page/`

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/ai-page/` | public | List AI pages |
| `POST` | `/api/ai-page/` | authenticated | Create an AI page (`title`, `description` 5–500 chars, `prompt` 5–1000 chars). The response contains the generated `html` |
| `GET` | `/api/ai-page/<id>/` | public | Retrieve an AI page |
| `PUT` / `PATCH` / `DELETE` | `/api/ai-page/<id>/` | owner or superuser | Update or delete an AI page |

Generation is synchronous: the `POST` returns after Gemini has responded, so expect a delay of a few seconds.

## Tests

```bash
export SECRET_KEY=test-secret-key-test-secret-key-0123456789 DEBUG=True \
  ALLOWED_HOSTS=testserver DATABASE_URL="sqlite:///:memory:" GEMINI_API_KEY=x

python manage.py test
```

The suite covers registration, password hashing, read and write permissions on users, privilege-escalation attempts and the privacy of public page listings. No external services are called.

## Data model

| Model | Fields |
|---|---|
| **Page** | `user`, `title`, `description`, `html`, timestamps |
| **AIPage** | `user`, `title`, `description`, `prompt`, `html` (filled by Gemini), timestamps |
| **User** | Django's built-in `auth.User` |

## Deployment

1. Set the variables from the configuration section; do **not** set `DEBUG` in production, and use a strong `SECRET_KEY`.
2. Set `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` to your real domains.
3. Run `python manage.py migrate` on each release.
4. Point `API_BASE` in `frontend/index.html` at your API and host the file on any static host.

> Pages are user-supplied HTML rendered by `/api/page/view/<id>/`. For a public deployment, serve that route from a **separate domain** from your API and frontend so that user scripts cannot reach their cookies or local storage.

## About

Built with Django REST Framework and Google Gemini.