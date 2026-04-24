from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash



def register_user(username, email, password):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # 🔍 Check if user already exists
    cursor.execute("SELECT * FROM profiles WHERE username=%s", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        return "exists"   # 🚨 important

    # 🔐 Hash password
    hashed_password = generate_password_hash(password)

    # ✅ Insert new user
    cursor.execute(
        "INSERT INTO profiles (username, email, password_hash) VALUES (%s,%s,%s)",
        (username, email, hashed_password)
    )
    db.commit()

    return "success"

def login_user(username, password):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM profiles WHERE username=%s", (username,))
    user = cursor.fetchone()

    if user and check_password_hash(user['password_hash'], password):
        return user

    return None