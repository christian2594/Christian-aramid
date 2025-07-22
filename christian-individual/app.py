from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"

# DB config
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="otoy"
)
cursor = db.cursor(dictionary=True)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    return render_template('dashboard.html', employees=employees)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    position = request.form['position']
    department = request.form['department']
    cursor.execute("INSERT INTO employees (name, position, department) VALUES (%s, %s, %s)",
                   (name, position, department))
    db.commit()
    return redirect(url_for('dashboard'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        department = request.form['department']
        cursor.execute("UPDATE employees SET name=%s, position=%s, department=%s WHERE id=%s",
                       (name, position, department, id))
        db.commit()
        return redirect(url_for('dashboard'))
    cursor.execute("SELECT * FROM employees WHERE id = %s", (id,))
    employee = cursor.fetchone()
    return render_template('edit.html', employee=employee)

@app.route('/delete/<int:id>')
def delete(id):
    cursor.execute("DELETE FROM employees WHERE id = %s", (id,))
    db.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
