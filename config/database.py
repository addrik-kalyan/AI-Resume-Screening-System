"""
config/database.py
-------------------
Lightweight JSON-file 'database' layer for Users and Jobs.

The project guide specifies MongoDB. To keep this project runnable instantly
on ANY machine (no MongoDB server required to install/run/test), this module
implements the exact same `users` / `jobs` collection shape as plain JSON
files under /database. If you want real MongoDB instead, set
USE_MONGO = True below and fill in MONGO_URI - the function signatures
(get_users, save_users, get_jobs, save_jobs) stay identical, so nothing
else in the app needs to change.
"""

import json
import os
import threading

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "database")
USERS_FILE = os.path.join(DB_DIR, "users.json")
JOBS_FILE = os.path.join(BASE_DIR, "model", "job_data.csv")

USE_MONGO = False
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "resume_screening_db"

_lock = threading.Lock()


def _ensure_users_file():
    os.makedirs(DB_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump([], f)


def get_users():
    """Return list of user dicts: {name, email, password(hash), role, resume, skills}"""
    _ensure_users_file()
    with _lock:
        with open(USERS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []


def save_users(users):
    _ensure_users_file()
    with _lock:
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)


def find_user_by_email(email):
    for u in get_users():
        if u.get("email", "").lower() == email.lower():
            return u
    return None


def add_user(user):
    users = get_users()
    users.append(user)
    save_users(users)


def update_user(email, updates):
    users = get_users()
    for u in users:
        if u.get("email", "").lower() == email.lower():
            u.update(updates)
            break
    save_users(users)


def delete_user(email):
    users = get_users()
    users = [u for u in users if u.get("email", "").lower() != email.lower()]
    save_users(users)


# ---- Jobs collection (kept in model/job_data.csv as required by the guide) ----

def get_jobs_df():
    import pandas as pd
    return pd.read_csv(JOBS_FILE)


def save_jobs_df(df):
    df.to_csv(JOBS_FILE, index=False)


if USE_MONGO:
    # Optional real MongoDB backend. Requires: pip install pymongo
    try:
        from pymongo import MongoClient

        _client = MongoClient(MONGO_URI)
        _mongo_db = _client[MONGO_DB_NAME]

        def get_users():  # noqa: F811
            return list(_mongo_db.users.find({}, {"_id": 0}))

        def add_user(user):  # noqa: F811
            _mongo_db.users.insert_one(user)

        def find_user_by_email(email):  # noqa: F811
            return _mongo_db.users.find_one({"email": email}, {"_id": 0})

        def update_user(email, updates):  # noqa: F811
            _mongo_db.users.update_one({"email": email}, {"$set": updates})

        def delete_user(email):  # noqa: F811
            _mongo_db.users.delete_one({"email": email})

    except ImportError:
        print("pymongo not installed - falling back to JSON file storage.")
