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
            departure_status TEXT NOT NULL,
            departure_lat REAL NOT NULL,
            departure_lon REAL NOT NULL,
            arrival_lat REAL NOT NULL,
            arrival_lon REAL NOT NULL
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

    # Add some sample flights with coordinates
    cursor.execute('INSERT INTO Flights (airline, flight_number, departure_time, departure_status, departure_lat, departure_lon, arrival_lat, arrival_lon) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                   ('Air Maldives', 'MV001', '2024-06-01 10:00', 'On Time', 4.1755, 73.5093, 40.7128, -74.0060))
    cursor.execute('INSERT INTO Flights (airline, flight_number, departure_time, departure_status, departure_lat, departure_lon, arrival_lat, arrival_lon) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                   ('Air Maldives', 'MV002', '2024-06-01 12:00', 'Delayed', 4.1755, 73.5093, 51.5074, -0.1278))

    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_type = request.form['user_type']
        password = request.form['password']

        id_prefix = None
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
        cursor.execute('SELECT COUNT(*) FROM Users WHERE user_type = ?', (user_type,))
        count = cursor.fetchone()[0]
        id = f"{id_prefix}{count+1:03d}"
        name = id

        password_hash = generate_password_hash(password)

        try:
            cursor.execute('INSERT INTO Users (id, name, password_hash, user_type) VALUES (?, ?, ?, ?)',
                           (id, name, password_hash, user_type))
            conn.commit()
            flash('Registration successful.', 'success')
        except sqlite3.IntegrityError as e:
            flash(f"An error occurred: {e}", 'error')
        finally:
            conn.close()

        return redirect(url_for('register'))  # Redirect to clear the form after successful registration
    
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
    flights = [{'id': row[0], 'airline': row[1], 'flight_number': row[2], 'departure_time': row[3], 'departure_status': row[4],
                'departure_lat': row[5], 'departure_lon': row[6], 'arrival_lat': row[7], 'arrival_lon': row[8]} for row in cursor.fetchall()]
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
            departure_lat = request.form['departure_lat']
            departure_lon = request.form['departure_lon']
            arrival_lat = request.form['arrival_lat']
            arrival_lon = request.form['arrival_lon']
            cursor.execute('INSERT INTO Flights (airline, flight_number, departure_time, departure_status, departure_lat, departure_lon, arrival_lat, arrival_lon) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                   (airline, flight_number, departure_time, departure_status, departure_lat, departure_lon, arrival_lat, arrival_lon))
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
