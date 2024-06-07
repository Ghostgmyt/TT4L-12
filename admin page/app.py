from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('admin.html')

@app.route('/dashboard')
def dashboard_page():
    return 'Welcome to the Dashboard Page!'

@app.route('/assign')
def pilots_page():
    return 'Weelcome to pilots page'


@app.route('/flights')
def flights_page():
    return 'Welcome to admin page'

@app.route('/chat')
def chat_page():
    return 'Welcome to the Chat Page!'

@app.route('/logout')
def logout():
    # Logic for logging out the user
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
