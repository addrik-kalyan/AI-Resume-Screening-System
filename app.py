"""
app.py
-------
AI-Based Resume Screening & Job Recommendation System
Main Flask application.

Workflow (per project guide):
  Module 1: User Registration/Login
  Module 2: Resume Upload
  Module 3: Resume Parser            (utils/resume_parser.py)
  Module 4: Skill Extraction (NLP)   (utils/skill_extractor.py)
  Module 5: Job Recommendation       (utils/recommendation.py)
  Module 6: Resume Scoring           (utils/recommendation.py)
  Module 7: Admin Module
"""

import os
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, send_from_directory
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from utils.resume_parser import extract_text
from utils.skill_extractor import extract_skills
from utils.recommendation import recommend_jobs
from config import database as db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "resumes")
ALLOWED_EXTENSIONS = {"pdf", "docx"}

app = Flask(__name__)
app.secret_key = "change-this-secret-key-in-production"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB max resume size

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --------------------------------------------------------------------------
# Seed a default admin account on first run (admin@resume.ai / admin123)
# --------------------------------------------------------------------------
def _seed_admin():
    if not db.find_user_by_email("admin@resume.ai"):
        db.add_user({
            "name": "Administrator",
            "email": "admin@resume.ai",
            "password": generate_password_hash("admin123"),
            "role": "admin",
            "resume": None,
            "skills": [],
        })


_seed_admin()


# --------------------------------------------------------------------------
# Helpers / decorators
# --------------------------------------------------------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_email" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Admin access only.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


# --------------------------------------------------------------------------
# Module 1: User Registration / Login
# --------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("register"))

        if db.find_user_by_email(email):
            flash("An account with that email already exists.", "error")
            return redirect(url_for("register"))

        db.add_user({
            "name": name,
            "email": email,
            "password": generate_password_hash(password),
            "role": "user",
            "resume": None,
            "skills": [],
        })
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = db.find_user_by_email(email)
        if user and check_password_hash(user["password"], password):
            session["user_email"] = user["email"]
            session["user_name"] = user["name"]
            session["role"] = user.get("role", "user")
            flash(f"Welcome back, {user['name']}!", "success")
            if session["role"] == "admin":
                return redirect(url_for("admin_panel"))
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


# --------------------------------------------------------------------------
# Module 2 + 3 + 4 + 5 + 6: Upload -> Parse -> Extract Skills -> Recommend -> Score
# --------------------------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    user = db.find_user_by_email(session["user_email"])
    return render_template("dashboard.html", user=user)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "GET":
        return render_template("upload_resume.html")

    if "resume" not in request.files:
        flash("No file selected.", "error")
        return redirect(url_for("upload"))

    file = request.files["resume"]

    if file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("upload"))

    if not allowed_file(file.filename):
        flash("Unsupported file type. Please upload a PDF or DOCX resume.", "error")
        return redirect(url_for("upload"))

    filename = secure_filename(f"{session['user_email']}_{file.filename}")
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(path)

    try:
        text = extract_text(path)                 # Module 3: Resume Parser
        skills = extract_skills(text)              # Module 4: Skill Extraction (NLP)
        jobs = recommend_jobs(skills, top_n=5)      # Module 5 + 6: Recommend + Score
    except Exception as e:
        flash(f"Could not process resume: {e}", "error")
        return redirect(url_for("upload"))

    db.update_user(session["user_email"], {"resume": filename, "skills": skills})

    return render_template("result.html", skills=skills, jobs=jobs)


# --------------------------------------------------------------------------
# Module 7: Admin Module (Add / Update / Delete jobs, View users)
# --------------------------------------------------------------------------
@app.route("/admin")
@admin_required
def admin_panel():
    jobs_df = db.get_jobs_df()
    users = [u for u in db.get_users() if u.get("role") != "admin"]
    return render_template(
        "admin.html",
        jobs=jobs_df.to_dict(orient="records"),
        users=users,
    )


@app.route("/admin/jobs/add", methods=["POST"])
@admin_required
def admin_add_job():
    jobs_df = db.get_jobs_df()
    new_row = {
        "job": request.form.get("job", "").strip(),
        "company": request.form.get("company", "").strip(),
        "skills": request.form.get("skills", "").strip().lower(),
        "description": request.form.get("description", "").strip(),
    }
    import pandas as pd
    jobs_df = pd.concat([jobs_df, pd.DataFrame([new_row])], ignore_index=True)
    db.save_jobs_df(jobs_df)

    from model.train_model import train
    train()  # retrain TF-IDF model so the new job is included in recommendations

    flash("Job added successfully.", "success")
    return redirect(url_for("admin_panel"))


@app.route("/admin/jobs/delete/<int:index>", methods=["POST"])
@admin_required
def admin_delete_job(index):
    jobs_df = db.get_jobs_df()
    if 0 <= index < len(jobs_df):
        jobs_df = jobs_df.drop(index).reset_index(drop=True)
        db.save_jobs_df(jobs_df)
        from model.train_model import train
        train()
        flash("Job deleted.", "success")
    return redirect(url_for("admin_panel"))


@app.route("/admin/jobs/update/<int:index>", methods=["POST"])
@admin_required
def admin_update_job(index):
    jobs_df = db.get_jobs_df()
    if 0 <= index < len(jobs_df):
        jobs_df.loc[index, "job"] = request.form.get("job", jobs_df.loc[index, "job"])
        jobs_df.loc[index, "company"] = request.form.get("company", jobs_df.loc[index, "company"])
        jobs_df.loc[index, "skills"] = request.form.get("skills", jobs_df.loc[index, "skills"]).lower()
        jobs_df.loc[index, "description"] = request.form.get("description", jobs_df.loc[index, "description"])
        db.save_jobs_df(jobs_df)
        from model.train_model import train
        train()
        flash("Job updated.", "success")
    return redirect(url_for("admin_panel"))


@app.route("/admin/users/delete/<email>", methods=["POST"])
@admin_required
def admin_delete_user(email):
    db.delete_user(email)
    flash("User removed.", "success")
    return redirect(url_for("admin_panel"))


# --------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
