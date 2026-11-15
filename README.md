# StudyHub — Student Management Portal

A beginner-friendly Flask and SQLite academic management application.

## Features
- User signup, login, logout, and password hashing
- Student CRUD (create, read, update, delete) and roll-number search
- Course CRUD
- Assignment CRUD, course association, due dates, and pending/completed status
- Dashboard statistics
- Responsive pastel-themed interface
- Dockerfile, Docker Compose, Nginx reverse proxy, and Jenkins pipeline example

## Run locally on Windows PowerShell

1. Open this folder in VS Code.
2. Create a virtual environment if needed:
   `py -m venv .venv`
3. Install requirements:
   `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
4. Start the app:
   `.\.venv\Scripts\python.exe app.py`
5. Open `http://127.0.0.1:5000`.
6. Create an account on the signup page.

## Existing database
The app uses `students.db` in the project folder. `CREATE TABLE IF NOT EXISTS` adds the new tables without deleting existing student rows. Keep a backup of `students.db` before changing database code.

## Docker
Install Docker Desktop, then run:
`docker compose up --build`

Open `http://localhost:8080`.

The included Compose file is a containerized Flask application behind Nginx. It is **not yet a microservices implementation**. A true microservices version requires splitting user, course, and assignment functionality into separately deployed services with service-specific APIs and data stores.

## Jenkins
The Jenkinsfile is a starter pipeline. A Jenkins agent needs Python, pip, and Docker installed and permission to use Docker. Configure a Jenkins Pipeline job pointing to this repository.

## Before public deployment
- Set a long random `SECRET_KEY` using an environment variable.
- Turn off Flask debug mode.
- Use HTTPS and secure cookie settings.
- Configure backups and production-grade database storage.
- Do not commit real passwords, secrets, or personal student data.
