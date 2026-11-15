import sqlite3
import os
from functools import wraps

from flask import (
    Flask, render_template, request, flash, redirect,
    url_for, session, g
)
from werkzeug.security import generate_password_hash, check_password_hash
import database as dt

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "local-development-key-change-before-deployment")

dt.create_database()

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user_id") is None:
            flash("Please log in to continue.", "info")
            return redirect(url_for("login"))
        g.user = dt.get_user_by_id(session["user_id"])
        if g.user is None:
            session.clear()
            return redirect(url_for("login"))
        return view(**kwargs)
    return wrapped_view

@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

# Authentication
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if len(username) < 3:
            flash("Username must contain at least 3 characters.", "error")
        elif len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        else:
            try:
                dt.create_user(username, generate_password_hash(password))
                flash("Account created. You can now log in.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("That username is already registered.", "error")
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = dt.get_user_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))
        flash("Incorrect username or password.", "error")
    return render_template("login.html")

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

# Dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", counts=dt.dashboard_counts())

# Students
@app.route("/students")
@login_required
def students():
    return render_template("students.html", students=dt.view_student())

@app.route("/students/add", methods=["GET", "POST"])
@login_required
def add_student():
    if request.method == "POST":
        name = request.form.get("name", "").strip().upper()
        roll_no = request.form.get("roll_no", "").strip().upper()
        branch = request.form.get("branch", "").strip().upper()
        try:
            cgpa = float(request.form.get("cgpa", ""))
        except ValueError:
            flash("Enter a valid CGPA.", "error")
            return render_template("student_form.html", student=None)
        if not name or not roll_no or not branch:
            flash("Please complete all fields.", "error")
        elif not 0 <= cgpa <= 10:
            flash("CGPA must be between 0 and 10.", "error")
        else:
            try:
                dt.insert_student(name, roll_no, branch, cgpa)
                flash("Student added successfully.", "success")
                return redirect(url_for("students"))
            except sqlite3.IntegrityError:
                flash("That roll number already exists.", "error")
    return render_template("student_form.html", student=None)

@app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    student = dt.get_student_by_id(student_id)
    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("students"))
    if request.method == "POST":
        name = request.form.get("name", "").strip().upper()
        roll_no = request.form.get("roll_no", "").strip().upper()
        branch = request.form.get("branch", "").strip().upper()
        try:
            cgpa = float(request.form.get("cgpa", ""))
        except ValueError:
            flash("Enter a valid CGPA.", "error")
            return render_template("student_form.html", student=student)
        if not name or not roll_no or not branch or not 0 <= cgpa <= 10:
            flash("Complete all fields and enter a CGPA from 0 to 10.", "error")
        else:
            try:
                dt.update_student(student_id, name, roll_no, branch, cgpa)
                flash("Student updated successfully.", "success")
                return redirect(url_for("students"))
            except sqlite3.IntegrityError:
                flash("That roll number is already used by another student.", "error")
    return render_template("student_form.html", student=student)

@app.route("/students/<int:student_id>/delete", methods=["POST"])
@login_required
def remove_student(student_id):
    student = dt.get_student_by_id(student_id)
    if student:
        dt.delete_student(student["roll_no"])
        flash("Student deleted.", "success")
    else:
        flash("Student not found.", "error")
    return redirect(url_for("students"))

@app.route("/students/search", methods=["GET", "POST"])
@login_required
def search_students():
    result = None
    if request.method == "POST":
        roll_no = request.form.get("roll_no", "").strip().upper()
        result = dt.search_student(roll_no)
        if result is None:
            flash("No student found with that roll number.", "info")
    return render_template("search_students.html", student=result)

# Courses
@app.route("/courses")
@login_required
def courses():
    return render_template("courses.html", courses=dt.view_courses())

@app.route("/courses/add", methods=["GET", "POST"])
@login_required
def add_course():
    if request.method == "POST":
        name = request.form.get("course_name", "").strip()
        code = request.form.get("course_code", "").strip().upper()
        semester = request.form.get("semester", "").strip()
        try:
            hours = int(request.form.get("credit_hours", ""))
        except ValueError:
            flash("Credit hours must be a whole number.", "error")
            return render_template("course_form.html", course=None)
        if not name or not code or not semester or hours <= 0:
            flash("Complete all fields and enter positive credit hours.", "error")
        else:
            try:
                dt.insert_course(name, code, hours, semester)
                flash("Course added successfully.", "success")
                return redirect(url_for("courses"))
            except sqlite3.IntegrityError:
                flash("That course code already exists.", "error")
    return render_template("course_form.html", course=None)

@app.route("/courses/<int:course_id>/edit", methods=["GET", "POST"])
@login_required
def edit_course(course_id):
    course = dt.get_course_by_id(course_id)
    if course is None:
        flash("Course not found.", "error")
        return redirect(url_for("courses"))
    if request.method == "POST":
        name = request.form.get("course_name", "").strip()
        code = request.form.get("course_code", "").strip().upper()
        semester = request.form.get("semester", "").strip()
        try:
            hours = int(request.form.get("credit_hours", ""))
        except ValueError:
            flash("Credit hours must be a whole number.", "error")
            return render_template("course_form.html", course=course)
        if not name or not code or not semester or hours <= 0:
            flash("Complete all fields and enter positive credit hours.", "error")
        else:
            try:
                dt.update_course(course_id, name, code, hours, semester)
                flash("Course updated successfully.", "success")
                return redirect(url_for("courses"))
            except sqlite3.IntegrityError:
                flash("That course code is already in use.", "error")
    return render_template("course_form.html", course=course)

@app.route("/courses/<int:course_id>/delete", methods=["POST"])
@login_required
def remove_course(course_id):
    if dt.delete_course(course_id):
        flash("Course deleted. Related assignments are kept without a course.", "success")
    else:
        flash("Course not found.", "error")
    return redirect(url_for("courses"))

# Assignments
@app.route("/assignments")
@login_required
def assignments():
    return render_template(
        "assignments.html",
        assignments=dt.view_assignments(),
        courses=dt.view_courses()
    )

@app.route("/assignments/add", methods=["GET", "POST"])
@login_required
def add_assignment():
    courses = dt.view_courses()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        course_id = request.form.get("course_id", "").strip()
        due_date = request.form.get("due_date", "").strip()
        if not title:
            flash("Assignment title is required.", "error")
        else:
            try:
                dt.insert_assignment(title, description, int(course_id) if course_id else None, due_date)
                flash("Assignment added successfully.", "success")
                return redirect(url_for("assignments"))
            except (ValueError, sqlite3.IntegrityError):
                flash("Please choose a valid course.", "error")
    return render_template("assignment_form.html", assignment=None, courses=courses)

@app.route("/assignments/<int:assignment_id>/edit", methods=["GET", "POST"])
@login_required
def edit_assignment(assignment_id):
    assignment = dt.get_assignment_by_id(assignment_id)
    if assignment is None:
        flash("Assignment not found.", "error")
        return redirect(url_for("assignments"))
    courses = dt.view_courses()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        course_id = request.form.get("course_id", "").strip()
        due_date = request.form.get("due_date", "").strip()
        status = request.form.get("status", "Pending")
        if not title or status not in ("Pending", "Completed"):
            flash("Enter a title and choose a valid status.", "error")
        else:
            try:
                dt.update_assignment(
                    assignment_id, title, description,
                    int(course_id) if course_id else None, due_date, status
                )
                flash("Assignment updated successfully.", "success")
                return redirect(url_for("assignments"))
            except (ValueError, sqlite3.IntegrityError):
                flash("Please choose a valid course.", "error")
    return render_template("assignment_form.html", assignment=assignment, courses=courses)

@app.route("/assignments/<int:assignment_id>/toggle", methods=["POST"])
@login_required
def toggle_assignment(assignment_id):
    assignment = dt.get_assignment_by_id(assignment_id)
    if assignment:
        new_status = "Completed" if assignment["status"] == "Pending" else "Pending"
        dt.set_assignment_status(assignment_id, new_status)
        flash(f"Assignment marked {new_status.lower()}.", "success")
    else:
        flash("Assignment not found.", "error")
    return redirect(url_for("assignments"))

@app.route("/assignments/<int:assignment_id>/delete", methods=["POST"])
@login_required
def remove_assignment(assignment_id):
    if dt.delete_assignment(assignment_id):
        flash("Assignment deleted.", "success")
    else:
        flash("Assignment not found.", "error")
    return redirect(url_for("assignments"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
