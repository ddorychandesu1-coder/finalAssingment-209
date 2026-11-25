# TaskManager

A Django web application for managing personal tasks. Users can register, organize tasks into projects and categories, filter and search them, and track progress on a dashboard.

## Features

- User registration, login and logout (custom user model)
- Task CRUD with priority, status and due dates
- Projects and categories (each user only sees their own data)
- Search, filters, sorting and pagination on the task list
- Dashboard with task counts, progress bar, overdue and due-today lists
- Profile page with avatar upload and password change
- Overdue highlighting and success/error messages

## Tech stack

- Python 3.14.6
- Django 6.1.3
- SQLite
- Bootstrap 5.3 (loaded from a CDN)
- Pillow (for avatar uploads)
## Setup

```bash
git clone https://github.com/ddorychandesu1-coder/finalAssingment-209.git
cd taskmanager
python -m venv .venv
source venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Run tests

```bash
python manage.py test
```

## Project structure

| Folder | Purpose |
|---|---|
| `config/` | Project settings and main URLs |
| `accounts/` | Custom user model, registration, profile |
| `tasks/` | Task, Project and Category models, forms and views |
| `core/` | Home page and dashboard |
| `templates/` | All HTML templates |

## Author

[Group memeber : - Ty David
                 - Sinoun Chanun 
                 - Run Ratha

Class : 209A]