from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

system = Flask(__name__)
bcrypt = Bcrypt(system)
system.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
system.config['SECRET_KEY'] = 'TT4L_12'
db = SQLAlchemy(system)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=7, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=7, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("This username already exists. Please try another name.")

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=7, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=7, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

@system.route('/')
def home():
    return render_template('home.html')

@system.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Add your login logic here
        pass
    return render_template('login.html', form=form)

@system.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

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
