
from flask import Flask, render_template, request, redirect, session,url_for
import pickle
import re
import numpy as np
from urllib.parse import urlparse
from auth import register_user, login_user
from db import get_db
rf_model = pickle.load(open("rf_model.pkl", "rb"))
import xgboost as xgb

xgb_model = xgb.Booster()
xgb_model.load_model("xgb_model.json")
# =========================
# FEATURE EXTRACTION
# =========================
def extract_features(url):
    features = []
    from urllib.parse import urlparse
    import re

    domain = urlparse(url).netloc

    # Basic
    features.append(len(url))
    features.append(url.count('.'))
    features.append(url.count('/'))

    # Suspicious symbols
    features.append(url.count('@'))
    features.append(url.count('-'))
    features.append(url.count('='))
    features.append(url.count('?'))

    # Digits & special chars
    features.append(sum(c.isdigit() for c in url))
    features.append(sum(not c.isalnum() for c in url))

    # Domain features
    features.append(len(domain))
    features.append(domain.count('.'))

    # IP address
    features.append(1 if re.search(r'(\d{1,3}\.){3}\d{1,3}', url) else 0)

    # HTTPS
    features.append(1 if url.startswith("https") else 0)

    # Keywords (STRONG SIGNAL)
    keywords = ['login','secure','verify','account','update','bank','signin','confirm','password']
    features.append(sum(word in url.lower() for word in keywords))

    # Shorteners
    shorteners = ['bit.ly','tinyurl','goo.gl','t.co','rb.gy']
    features.append(1 if any(s in url for s in shorteners) else 0)

    # Suspicious TLDs (NEW 🔥)
    tlds = ['.tk','.ml','.ga','.cf','.gq']
    features.append(1 if any(t in url for t in tlds) else 0)

    return features

app = Flask(__name__)
app.secret_key = "secret123"

# ✅ HOME PAGE
@app.route('/')
def index():
    return redirect('/home')

@app.route('/home')
def home():
    return render_template('home.html')


# ✅ LOGIN
from auth import login_user


from flask import session, redirect, url_for, render_template

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = login_user(username, password)

        if user:
            session['user_id'] = user['id'] 
            return redirect(url_for('predict_page'))
        else:
            session['error'] = "Wrong username or password"   # ✅ store message
            return redirect(url_for('login'))  # redirect (important)

    error = session.pop('error', None)  # ✅ get once
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    errors = []
    success = None
    exists = None

    username = ""
    email = ""

    if request.method == 'POST':

        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        # ================= VALIDATION =================
        if not re.match(r'^[A-Za-z0-9_]{6,15}$', username):
            errors.append("Username must be 6–15 characters (letters, numbers, _)")

        email_pattern = r'^[\w\.-]+@(gmail\.com|outlook\.com|yahoo\.com|hotmail\.com)$'
        if not re.match(email_pattern, email):
            errors.append("Use valid email domain (gmail.com, outlook.com, yahoo.com)")

        if len(password) < 8:
            errors.append("Password must be at least 8 characters")

        if not re.search(r'[A-Z]', password):
            errors.append("Password must include 1 uppercase letter")

        if not re.search(r'[a-z]', password):
            errors.append("Password must include 1 lowercase letter")

        if not re.search(r'[0-9]', password):
            errors.append("Password must include 1 number")

        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            errors.append("Password must include 1 special character")

        # ================= SHOW ERRORS =================
        if errors:
            return render_template(
                "register.html",
                errors=errors,
                username=username,
                email=email
            )

        # ================= DB INSERT =================
        result = register_user(username, email, password)

        if result == "username_exists":
            return render_template("register.html", error="Username already exists")

        if result == "email_exists":
            return render_template("register.html", error="Email already registered")

        if result == "success":
            return redirect(url_for('login'))
        return render_template(
            "register.html",
            errors=errors,
            username=username,
            email=email
        )
    return render_template("register.html")
def register_user(username, email, password):
    db = get_db()
    cursor = db.cursor()

    try:
        # check username exists
        cursor.execute("SELECT id FROM profile WHERE username=%s", (username,))
        if cursor.fetchone():
            return "username_exists"

        # check email exists
        cursor.execute("SELECT id FROM profile WHERE email=%s", (email,))
        if cursor.fetchone():
            return "email_exists"

        # insert user
        cursor.execute(
            "INSERT INTO profile (username, email, password, created_at) VALUES (%s, %s, %s, NOW())",
            (username, email, password)
        )

        db.commit()
        return "success"

    except Exception as e:
        print("DB ERROR:", e)
        return "error"

    finally:
        cursor.close()
        db.close()



# ✅ PREDICT PAGE
@app.route('/predict')
def predict_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('predict.html')


@app.route('/result', methods=['GET','POST'])
def result():
    if 'user_id' not in session:
        return redirect('/login')

    url = request.form.get('url', '').strip()

    result = None
    warning = None
    score = None
    reasons = []   # ✅ ADD HERE

    if url:
        # ✅ extract features
        features = extract_features(url)
        dmatrix = xgb.DMatrix([features])

        # ✅ model predictions
        rf_score = rf_model.predict_proba([features])[0][1]
        xgb_score = xgb_model.predict(dmatrix)[0]

        # ✅ final score
        score = (rf_score + xgb_score) / 2 * 100
        score = round(score, 2)

        # ✅ classification
        if score < 50:
            result = "Safe"
        elif score < 75:
            result = "Suspicious"
        else:
            result = "Dangerous"
        from db import get_db

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO history (user_id, url, score, status) VALUES (%s, %s, %s, %s)",
            (session['user_id'], url, score, result)
        )

        db.commit()
        cursor.close()
        db.close()
        # 🚀 ADD REASONS HERE (INSIDE if url)
        url_lower = url.lower()

        keywords = ['login','verify','account','update','bank','signin']
        for word in keywords:
            if word in url_lower:
                reasons.append(f"Contains suspicious keyword: '{word}'")

        if any(s in url_lower for s in ['bit.ly','tinyurl','t.co','goo.gl']):
            reasons.append("Uses URL shortener")

        import re
        if re.search(r'(\d{1,3}\.){3}\d{1,3}', url):
            reasons.append("Contains IP address")

        if url.count('.') > 3:
            reasons.append("Too many subdomains")

        if len(url) > 75:
            reasons.append("URL is too long")

        if '@' in url:
            reasons.append("Contains '@' symbol")

        if '-' in url:
            reasons.append("Contains '-' in domain")

        if url.startswith("http://"):
            reasons.append("Not using HTTPS")

        if sum(c.isdigit() for c in url) > 5:
            reasons.append("Too many numbers in URL")

        if any(t in url_lower for t in ['.tk','.ml','.ga','.cf','.gq']):
            reasons.append("Suspicious domain extension")

        # ✅ LIMIT reasons (clean UI)
        reasons = reasons[:3]

        if result == "Safe":
            reasons = ["No major risks detected"]   # ✅ only this message
        else:
            if not reasons:
                reasons = ["Potential risks detected"]  
    return render_template(
        'result.html',
        url=url,
        result=result,
        warning=warning,
        score=score,
        reasons=reasons   # ✅ PASS HERE
    )
@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect('/login')

    from db import get_db

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT url, score, status, created_at FROM history WHERE user_id=%s ORDER BY created_at DESC",
        (session['user_id'],)
    )

    history_data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('history.html', history=history_data)
if __name__ == "__main__":
    app.run(debug=True)