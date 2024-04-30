from flask import Flask , render_template , url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

system = Flask(__name__)
system.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
system.config['SECRET_KEY'] = 'TT4L_12'
db = SQLAlchemy(system)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(60), nullable=False)

@system.route('/')
def home():
    return render_template('home.html')

@system.route('/login')
def login():
    return render_template('login.html')

@system.route('/register')
def register():
    return render_template('register.html')

@system.route('/admin')
def admin():
    return render_template('admin.html')

@system.route('/flight_tracker')
def flight_tracker():
    return render_template('flight_tracker.html')

@system.route('/about')
def about():
    return render_template('about.html')



if __name__ == '__main__':
    system.run(debug=True)
    


