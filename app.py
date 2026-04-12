import os
from flask import Flask, render_template, request, session, redirect, url_for
from dotenv import load_dotenv

# 1. Load secret key from app.env
load_dotenv(dotenv_path='app.env')

# 2. Setup Flask to look for HTML in the current folder
app = Flask(__name__, template_folder='.')
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key_12345')

@app.route('/')
def home():
    # Flask will now find templates.html in this folder
    user = session.get('user')
    return render_template('templates.html', user=user)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    if username:
        session['user'] = username
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    # Correct syntax to end session
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)