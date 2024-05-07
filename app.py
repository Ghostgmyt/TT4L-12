from flask import Flask, render_template, request, redirect, url_for

# Create Flask application instance and specify the template folder
app = Flask(__name__, template_folder='C:/Users/ASUS/Desktop/Website/templates', static_folder='C:/Users/ASUS/Desktop/Website/static')

# Mock database to store user credentials (replace with your actual database)
users = {
    'user1@example.com': 'password1',
    'user2@example.com': 'password2'
}

# Define routes and corresponding view functions
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/flight_tracker')
def flight_tracker():
    return render_template('flight_tracker.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the email and password from the form
        email = request.form['email']
        password = request.form['password']
        
        # Check if the email exists in the database and if the password matches
        if email in users and users[email] == password:
            # Redirect to home page after successful login
            return redirect(url_for('home'))
        else:
            # If login fails, reload the login page with an error message
            return render_template('login.html', error='Invalid email or password')
    
    # Render the login form
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/commands1')
def commands1():
    return render_template('commands1.html')

@app.route('/commands2')
def commands2():
    return render_template('commands2.html')

@app.route('/commands3')
def commands3():
    return render_template('commands3.html')

if __name__ == '__main__':
    app.run(debug=True)
