from flask import Flask, render_template, request, redirect, session
from features import extract_features
from model import predict
from auth import register_user, login_user
from db import get_db
import csv

app = Flask(__name__)
app.secret_key = "secret123"
@app.route('/')
def index():
    return redirect('/home')
from flask import Flask, render_template, request, redirect, session, flash
from auth import login_user

app = Flask(__name__)
app.secret_key = "your_secret_key"

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = login_user(username, password)
        if user:
            session['user_id'] = user['id']  # use id from profiles
            return redirect('/predict')      # 🔹 go directly to predict page
        else:
            flash("Invalid username or password", "danger")
            return redirect('/login')

    return render_template('login.html')

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/')

    score = None
    status = None
    color = None

    if request.method == 'POST':
        url = request.form['url']
        features = extract_features(url)
        result, score = predict(features)

        # ✅ KEEP THIS INSIDE POST
        if score < 40:
            status = "Safe"
            color = "#22c55e"
        elif score < 70:
            status = "Suspicious"
            color = "#f59e0b"
        else:
            status = "Dangerous"
            color = "#ef4444"

        # ✅ SAVE TO DB
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO history (user_id, url, score, status) VALUES (%s,%s,%s,%s)",
            (session['user_id'], url, score, status)
        )
        db.commit()
        cursor.close()
        db.close()

    # ✅ FETCH HISTORY (outside POST is correct)
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT url, score, status, created_at FROM history WHERE user_id=%s",
        (session['user_id'],)
    )
    history = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template(
        'dashboard.html',
        score=score,
        status=status,
        color=color,
        history=history
    )
@app.route('/home')
def home():
    return render_template('home.html')
   



 
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        register_user(
            request.form['username'],
            request.form['email'],
            request.form['password']
        )
        return redirect('/')
    return render_template('register.html')
@app.route('/predict')
def predict_page():
    return render_template('predict.html')


@app.route('/result', methods=['POST'])
def result():
    # check if user is logged in
    if 'user_id' not in session:
        return redirect('/login')

    # get URL from form
    url = request.form.get('url', '').strip()
    result = None
    warning = None

    if url:
        url_lower = url.lower()

        if any(word in url_lower for word in ["phish", "malware", "danger"]):
            result = "Phishing"
            warning = "⚠️ This link is dangerous! Do not click it."
        elif url_lower.startswith("https://"):
            result = "Safe"
        else:
            result = "Suspicious"
            warning = "⚠️ Be careful with this link!"

    return render_template('result.html', url=url, result=result, warning=warning)

if __name__ == "__main__":
    app.run(debug=True)