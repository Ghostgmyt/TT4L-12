from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '1997019970'

# Initialize the database with new tables and sample data
def init_db():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS Users')
    cursor.execute('DROP TABLE IF EXISTS Flights')

    cursor.execute('''
        CREATE TABLE Users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            user_type TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE Flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            airline TEXT NOT NULL,
            flight_number TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            departure_status TEXT NOT NULL
        )
    ''')

    cursor.execute('INSERT INTO Users (id, name, password_hash, user_type) VALUES (?, ?, ?, ?)',
                   ('A001', 'AdminUser1', generate_password_hash('adminpass1'), 'admin'))
    cursor.execute('INSERT INTO Users (id, name, password_hash, user_type) VALUES (?, ?, ?, ?)',
                   ('A002', 'AdminUser2', generate_password_hash('adminpass2'), 'admin'))
    cursor.execute('INSERT INTO Users (id, name, password_hash, user_type) VALUES (?, ?, ?, ?)',
                   ('P001', 'PilotUser1', generate_password_hash('pilotpass1'), 'pilot'))
    cursor.execute('INSERT INTO Users (id, name, password_hash, user_type) VALUES (?, ?, ?, ?)',
                   ('P002', 'PilotUser2', generate_password_hash('pilotpass2'), 'pilot'))
    cursor.execute('INSERT INTO Users (id, name, password_hash, user_type) VALUES (?, ?, ?, ?)',
                   ('C001', 'ATCUser1', generate_password_hash('atcpass1'), 'atcontrol'))
    cursor.execute('INSERT INTO Users (id, name, password_hash, user_type) VALUES (?, ?, ?, ?)',
                   ('C002', 'ATCUser2', generate_password_hash('atcpass2'), 'atcontrol'))

    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        id_prefix = None
        user_type = None

        id = request.form['id']
        password = request.form['password']
        user_type = request.form['user_type']

        if user_type == 'admin':
            id_prefix = 'A'
        elif user_type == 'pilot':
            id_prefix = 'P'
        elif user_type == 'atcontrol':
            id_prefix = 'C'
        else:
            flash('Invalid user type selected.', 'error')
            return render_template('register.html')

        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM Users WHERE user_type = '{user_type}'")
        count = cursor.fetchone()[0]
        id = f"{id_prefix}{count+1:03d}"
        name = id

        password_hash = generate_password_hash(password)

        try:
            cursor.execute('INSERT INTO Users (id, name, password_hash, user_type) VALUES (?, ?, ?, ?)',
                           (id, name, password_hash, user_type))
            conn.commit()
            conn.close()
            flash('Registration successful.', 'success')
        except sqlite3.IntegrityError as e:
            flash(f"An error occurred: {e}", 'error')
            return render_template('register.html')

        return redirect('/register')  # Redirect to clear the form after successful registration
    
    return render_template('register.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/flights')
def flights():
    return render_template('flights.html')

@app.route('/get_flights')
def get_flights():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Flights')
    flights = [{'airline': row[1], 'flight_number': row[2], 'departure_time': row[3], 'departure_status': row[4],
                'departure_city': row[5], 'departure_lat': row[6], 'departure_lon': row[7],
                'arrival_city': row[8], 'arrival_lat': row[9], 'arrival_lon': row[10]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(flights)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()
        
        if 'add' in request.form:
            airline = request.form['airline']
            flight_number = request.form['flight_number']
            departure_time = request.form['departure_time']
            departure_status = request.form['departure_status']
            cursor.execute('INSERT INTO Flights (airline, flight_number, departure_time, departure_status) VALUES (?, ?, ?, ?)',
                           (airline, flight_number, departure_time, departure_status))
            flash('Flight added successfully.', 'success')
        
        elif 'remove' in request.form:
            flight_id = request.form['remove']
            cursor.execute('DELETE FROM Flights WHERE id = ?', (flight_id,))
            flash('Flight removed successfully.', 'success')
        
        elif 'edit' in request.form:
            flight_id = request.form['edit']
            airline = request.form['airline']
            flight_number = request.form['flight_number']
            departure_time = request.form['departure_time']
            departure_status = request.form['departure_status']
            cursor.execute('UPDATE Flights SET airline = ?, flight_number = ?, departure_time = ?, departure_status = ? WHERE id = ?',
                           (airline, flight_number, departure_time, departure_status, flight_id))
            flash('Flight updated successfully.', 'success')
        
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))
    
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Flights')
    table_data = cursor.fetchall()
    conn.close()
    
    return render_template('admin.html', table_data=table_data)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['id']
    password = request.form['password']

    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, name, password_hash, user_type FROM Users WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    conn.close()

    if user and check_password_hash(user[2], password):
        if user[3] == 'admin':
            return redirect(url_for('admin'))
        elif user[3] == 'pilot':
            return redirect(url_for('pilot'))
        elif user[3] == 'atcontrol':
            return redirect(url_for('atcontrol'))
    else:
        flash('Invalid credentials.', 'error')
        return redirect(url_for('home'))

@app.route('/pilot')
def pilot():
    return render_template('pilot.html')

@app.route('/atcontrol')
def atcontrol():
    return render_template('atcontrol.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
