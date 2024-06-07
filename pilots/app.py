from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('pilotshome.html')

@app.route('/My_flights')
def duty_roster():
    return render_template('My_flights.html')

@app.route('/chat')
def chat():
    return 'Welcome to the Chat Page!'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)






