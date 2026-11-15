import os
import sqlite3
from contextlib import closing

DATA_DIR = os.environ.get("DATA_DIR", ".")
os.makedirs(DATA_DIR, exist_ok=True)
DATABASE_NAME = os.path.join(DATA_DIR, "students.db")

def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_database():
    with closing(get_connection()) as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL UNIQUE,
            branch TEXT NOT NULL,
            cgpa REAL NOT NULL CHECK(cgpa >= 0 AND cgpa <= 10)
        );

        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            course_code TEXT NOT NULL UNIQUE,
            credit_hours INTEGER NOT NULL CHECK(credit_hours > 0),
            semester TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            course_id INTEGER,
            due_date TEXT,
            status TEXT NOT NULL DEFAULT 'Pending'
                CHECK(status IN ('Pending', 'Completed')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE SET NULL
        );
        """)
        conn.commit()

# Users
def create_user(username, password_hash):
    with closing(get_connection()) as conn:
        cur = conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()
        return cur.lastrowid

def get_user_by_username(username):
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

def get_user_by_id(user_id):
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT id, username FROM users WHERE id = ?", (user_id,)
        ).fetchone()

# Students
def insert_student(name, roll_no, branch, cgpa):
    with closing(get_connection()) as conn:
        cur = conn.execute(
            """INSERT INTO students (name, roll_no, branch, cgpa)
               VALUES (?, ?, ?, ?)""",
            (name, roll_no, branch, cgpa)
        )
        conn.commit()
        return cur.lastrowid

def view_student():
    with closing(get_connection()) as conn:
        return conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()

def total_students():
    with closing(get_connection()) as conn:
        return conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]

def search_student(roll_no):
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT * FROM students WHERE roll_no = ?", (roll_no,)
        ).fetchone()

def get_student_by_id(student_id):
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT * FROM students WHERE id = ?", (student_id,)
        ).fetchone()

def update_student(student_id, name, roll_no, branch, cgpa):
    with closing(get_connection()) as conn:
        conn.execute(
            """UPDATE students SET name=?, roll_no=?, branch=?, cgpa=?
               WHERE id=?""",
            (name, roll_no, branch, cgpa, student_id)
        )
        conn.commit()

def delete_student(roll_no):
    with closing(get_connection()) as conn:
        cur = conn.execute("DELETE FROM students WHERE roll_no = ?", (roll_no,))
        conn.commit()
        return cur.rowcount > 0

# Courses
def insert_course(course_name, course_code, credit_hours, semester):
    with closing(get_connection()) as conn:
        cur = conn.execute(
            """INSERT INTO courses (course_name, course_code, credit_hours, semester)
               VALUES (?, ?, ?, ?)""",
            (course_name, course_code, credit_hours, semester)
        )
        conn.commit()
        return cur.lastrowid

def view_courses():
    with closing(get_connection()) as conn:
        return conn.execute("SELECT * FROM courses ORDER BY id DESC").fetchall()

def get_course_by_id(course_id):
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT * FROM courses WHERE id = ?", (course_id,)
        ).fetchone()

def update_course(course_id, course_name, course_code, credit_hours, semester):
    with closing(get_connection()) as conn:
        conn.execute(
            """UPDATE courses SET course_name=?, course_code=?,
               credit_hours=?, semester=? WHERE id=?""",
            (course_name, course_code, credit_hours, semester, course_id)
        )
        conn.commit()

def delete_course(course_id):
    with closing(get_connection()) as conn:
        cur = conn.execute("DELETE FROM courses WHERE id = ?", (course_id,))
        conn.commit()
        return cur.rowcount > 0

# Assignments
def insert_assignment(title, description, course_id, due_date):
    with closing(get_connection()) as conn:
        cur = conn.execute(
            """INSERT INTO assignments (title, description, course_id, due_date)
               VALUES (?, ?, ?, ?)""",
            (title, description, course_id or None, due_date or None)
        )
        conn.commit()
        return cur.lastrowid

def view_assignments():
    with closing(get_connection()) as conn:
        return conn.execute("""
            SELECT a.*, c.course_name, c.course_code
            FROM assignments a
            LEFT JOIN courses c ON c.id = a.course_id
            ORDER BY
              CASE WHEN a.status = 'Pending' THEN 0 ELSE 1 END,
              a.due_date IS NULL, a.due_date, a.id DESC
        """).fetchall()

def get_assignment_by_id(assignment_id):
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT * FROM assignments WHERE id = ?", (assignment_id,)
        ).fetchone()

def update_assignment(assignment_id, title, description, course_id, due_date, status):
    with closing(get_connection()) as conn:
        conn.execute(
            """UPDATE assignments
               SET title=?, description=?, course_id=?, due_date=?, status=?
               WHERE id=?""",
            (title, description, course_id or None, due_date or None, status, assignment_id)
        )
        conn.commit()

def set_assignment_status(assignment_id, status):
    with closing(get_connection()) as conn:
        conn.execute(
            "UPDATE assignments SET status=? WHERE id=?",
            (status, assignment_id)
        )
        conn.commit()

def delete_assignment(assignment_id):
    with closing(get_connection()) as conn:
        cur = conn.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))
        conn.commit()
        return cur.rowcount > 0

def dashboard_counts():
    with closing(get_connection()) as conn:
        cur = conn.cursor()
        return {
            "students": cur.execute("SELECT COUNT(*) FROM students").fetchone()[0],
            "courses": cur.execute("SELECT COUNT(*) FROM courses").fetchone()[0],
            "assignments": cur.execute("SELECT COUNT(*) FROM assignments").fetchone()[0],
            "pending": cur.execute(
                "SELECT COUNT(*) FROM assignments WHERE status='Pending'"
            ).fetchone()[0],
            "completed": cur.execute(
                "SELECT COUNT(*) FROM assignments WHERE status='Completed'"
            ).fetchone()[0],
        }
