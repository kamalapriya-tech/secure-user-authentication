from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()  # Only works locally if .env file is present

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "KP")

# MySQL connection using environment variables
conn = mysql.connector.connect(
    host=os.environ.get("DB_HOST"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    database=os.environ.get("DB_NAME")
)
cursor = conn.cursor(dictionary=True)
# Home/Login page
@app.route('/')
def home():
    return render_template('login.html')

# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute("SELECT * FROM users2 WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            return "Email already registered! <a href='/register'>Try again</a>"

        try:
            cursor.execute(
                "INSERT INTO users2 (username, email, password) VALUES (%s, %s, %s)",
                (username, email, password)
            )
            conn.commit()
        except mysql.connector.Error as err:
            cursor.close()
            return f"Error inserting user: {err}"

        cursor.close()
        return redirect(url_for('home'))

    return render_template('register.html')

# Login form submit
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users2 WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()

    if user and check_password_hash(user[3], password):  # user[3] = password column
        session['username'] = user[1]  # user[1] = username
        return redirect(url_for('dashboard'))

    return 'Invalid credentials. <a href="/">Try again</a>'

# Dashboard (protected)
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('home'))

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
