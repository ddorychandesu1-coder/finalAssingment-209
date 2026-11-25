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

- Python [your version], Django [your version]
- SQLite
- Bootstrap 5 (CDN)

## Setup

```bash
git clone [your repo link, or just unzip the project]
cd taskmanager
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
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

- `accounts/`: custom user, register, profile
- `tasks/`: Task, Project, Category models and views
- `core/`: home page and dashboard
- `templates/`: all HTML templates

## Screenshots

[Add images here: dashboard, task list, task form, projects]

## Author

[Group memeber : - Ty David
                 - Sinoun Chanun 
                 - Run Ratha
Class : 209A]