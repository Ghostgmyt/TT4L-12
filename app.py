from flask import Flask, render_template, request, redirect, flash, url_for, jsonify, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
app.secret_key = '1997019970'
app.config['SECRET_KEY'] = 'your_secret_key_here'
socketio = SocketIO(app)
start_time = datetime.now()

DB_FILE = 'my_database.db'

def get_flights_for_user(user_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Flights WHERE pilot_id = ?', (user_id,))
    flights = cursor.fetchall()
    conn.close()
    return flights

@app.route('/get_flights')
def get_flights():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Flights')
    flights = cursor.fetchall()
    conn.close()

    flights_list = []
    for flight in flights:
        flight_dict = {
            'airline': flight[1],
            'flight_number': flight[2],
            'departure_time': flight[3],
            'departure_status': flight[4],
            'departure_lat': flight[5],
            'departure_lon': flight[6],
            'arrival_lat': flight[7],
            'arrival_lon': flight[8]
        }
        flights_list.append(flight_dict)
    return jsonify(flights_list)

def get_virtual_time():
    now = datetime.now()
    virtual_elapsed = now - start_time
    virtual_time = start_time + virtual_elapsed
    return virtual_time

def create_tables():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    accepted BOOLEAN DEFAULT 0
                 )''')
    conn.commit()
    conn.close()

create_tables()

instruction_map = {
    'Departure': {
        'Pushback': 'Pushback approved',
        'Taxi': 'Taxi to runway 32R, via taxiway Alpha, Bravo',
        'Takeoff': 'Winds 320 at 10, runway 32R, cleared for takeoff',
        'Requesting engine start': 'Engine start approved',
        'Preflight checks complete': 'Cleared for pushback and engine start',
    },
    'Landing': {
        'Ready for landing': 'Cleared to land runway 32R',
        'Clear of the runway': 'Taxi to gate B7',
    },
    'Emergencies': {
        'Emergency declaration': 'Roger your Mayday. What is your request?',
        'Request landing': 'Emergency services are standing by.',
        'Requesting assistance and instructions': 'I have cleared airspace for your emergency descent. Nearest suitable airport is 20 miles northwest. I will provide vectors for approach. Emergency services have been alerted. Confirm souls on board and fuel remaining.',
    },
    'Miscellaneous': {
        'Requesting diversion': 'Cleared to alternate airport',
        'Weather alert': 'Turn 270',
        'Navigation system down': 'Turn right heading 180 for vectors',
    }
}

@app.route('/chat_home')
def chat_home():
    return render_template('chat_home.html')

@app.route('/chat/<role>')
def chat(role):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM messages ORDER BY timestamp")
    rows = c.fetchall()
    messages = []
    for row in rows:
        messages.append({
            'id': row[0],
            'role': row[1],
            'message': row[2],
            'timestamp': row[3],
            'accepted': row[4]
        })
    conn.close()
    return render_template('chat.html', role=role, messages=messages, instruction_map=instruction_map)

@app.route('/fetch_messages')
def fetch_messages():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM messages ORDER BY timestamp")
    rows = c.fetchall()
    messages = []
    for row in rows:
        messages.append({
            'id': row[0],
            'role': row[1],
            'message': row[2],
            'timestamp': row[3],
            'accepted': row[4]
        })
    conn.close()
    return jsonify(messages)

@socketio.on('send_message')
def send_message(data):
    role = data['role']
    if role == 'Pilot':
        instruction = data['instruction']
        message = instruction
    else:
        message = data['message']
        for category, instructions in instruction_map.items():
            if message in instructions:
                message = instructions[message]
                break
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO messages (role, message) VALUES (?, ?)", (role, message))
    conn.commit()
    conn.close()
    socketio.emit('new_message', {
        'role': role,
        'message': message,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'id': None,
        'accepted': False
    }, broadcast=True)

@socketio.on('accept_message')
def accept_message(message_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE messages SET accepted = 1 WHERE id = ?", (message_id,))
    conn.commit()
    c.execute("SELECT * FROM messages WHERE id = ?", (message_id,))
    row = c.fetchone()
    if row:
        message = row[2]
        for category, instructions in instruction_map.items():
            if message in instructions:
                response_message = instructions[message]
                c.execute("INSERT INTO messages (role, message) VALUES (?, ?)", ('ATC', response_message))
                conn.commit()
                socketio.emit('new_message', {
                    'role': 'ATC',
                    'message': response_message,
                    'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    'id': None,
                    'accepted': False
                }, broadcast=True)
                break
    conn.close()

def init_db():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS Users')
    cursor.execute('DROP TABLE IF EXISTS Flights')
    cursor.execute('DROP TABLE IF EXISTS PilotFlightAssignment')

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
            arrival_lon REAL NOT NULL,
            pilot_id TEXT  -- This line adds the new column
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

        if user_type == 'admin':
            return redirect(url_for('admin'))
        elif user_type == 'pilot':
            return redirect(url_for('pilot'))
        elif user_type == 'atcontrol':
            return redirect(url_for('atcontrol'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']

        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE id = ?', (id,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            flash('Login successful!', 'success')
            user_type = user[3]
            if user_type == 'admin':
                return redirect(url_for('admin_home'))
            elif user_type == 'pilot':
                session['user_id'] = id  
                return redirect(url_for('pilot'))  
            elif user_type == 'atcontrol':
                return redirect(url_for('chat', role='ATC'))
        else:
            flash('Invalid ID or password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if 'add' in request.form:
            airline = request.form['airline']
            flight_number = request.form['flight_number']
            departure_time = request.form['departure_time']
            departure_status = request.form['departure_status']
            departure_lat = request.form['departure_lat']
            departure_lon = request.form['departure_lon']
            arrival_lat = request.form['arrival_lat']
            arrival_lon = request.form['arrival_lon']

            conn = sqlite3.connect('my_database.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Flights (airline, flight_number, departure_time, departure_status, departure_lat, departure_lon, arrival_lat, arrival_lon) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                           (airline, flight_number, departure_time, departure_status, departure_lat, departure_lon, arrival_lat, arrival_lon))
            conn.commit()
            conn.close()
            flash('Flight added successfully', 'success')

        elif 'remove' in request.form:
            flight_id = request.form['remove']
            conn = sqlite3.connect('my_database.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Flights WHERE id = ?", (flight_id,))
            conn.commit()
            conn.close()
            flash('Flight removed successfully', 'success')

        elif 'edit' in request.form:
            flight_id = request.form['edit']
            flash('Flight edited successfully', 'success')

    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Flights")
    table_data = cursor.fetchall()
    conn.close()

    virtual_time = get_virtual_time().strftime('%Y-%m-%d %H:%M:%S')
    return render_template('admin.html', table_data=table_data, current_time=virtual_time)

@app.route('/add_flight', methods=['POST'])
def add_flight():
    airline = request.form['airline']
    flight_number = request.form['flight_number']
    departure_time = request.form['departure_time']
    departure_status = request.form['departure_status']
    departure_lat = request.form['departure_lat']
    departure_lon = request.form['departure_lon']
    arrival_lat = request.form['arrival_lat']
    arrival_lon = request.form['arrival_lon']

    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Flights (airline, flight_number, departure_time, departure_status, departure_lat, departure_lon, arrival_lat, arrival_lon)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (airline, flight_number, departure_time, departure_status, departure_lat, departure_lon, arrival_lat, arrival_lon))
    conn.commit()
    conn.close()

    return redirect(url_for('admin'))

@app.route('/edit_flight/<int:flight_id>', methods=['GET', 'POST'])
def edit_flight(flight_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        airline = request.form['airline']
        flight_number = request.form['flight_number']
        departure_time = request.form['departure_time']
        departure_status = request.form['departure_status']
        departure_lat = request.form['departure_lat']
        departure_lon = request.form['departure_lon']
        arrival_lat = request.form['arrival_lat']
        arrival_lon = request.form['arrival_lon']

        cursor.execute('''
            UPDATE Flights
            SET airline = ?, flight_number = ?, departure_time = ?, departure_status = ?, departure_lat = ?, departure_lon = ?, arrival_lat = ?, arrival_lon = ?
            WHERE id = ?
        ''', (airline, flight_number, departure_time, departure_status, departure_lat, departure_lon, arrival_lat, arrival_lon, flight_id))
        conn.commit()
        conn.close()
        flash('Flight updated successfully', 'success')
        return redirect(url_for('admin'))

    else:
        cursor.execute('SELECT * FROM Flights WHERE id = ?', (flight_id,))
        flight = cursor.fetchone()
        conn.close()
        if flight:
            flight_data = {
                'id': flight[0],
                'airline': flight[1],
                'flight_number': flight[2],
                'departure_time': flight[3],
                'departure_status': flight[4],
                'departure_lat': flight[5],
                'departure_lon': flight[6],
                'arrival_lat': flight[7],
                'arrival_lon': flight[8]
            }
            return render_template('edit_flight.html', flight=flight_data)
        else:
            flash('Flight not found', 'error')
            return redirect(url_for('admin'))

@app.route('/delete_flight/<int:flight_id>', methods=['POST'])
def delete_flight(flight_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Flights WHERE id = ?', (flight_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('admin'))

@app.route('/pilot')
def pilot():
    return render_template('pilot.html')

@app.route('/my_flights')
def my_flights():
    user_id = session.get('user_id')
    if user_id:
        # Fetch flights for the logged-in user from the database
        flights = get_flights_for_user(user_id)
        return render_template('my_flights.html', flights=flights)
    else:
        return redirect(url_for('login'))


@app.route('/assign', methods=['GET', 'POST'])
def assign():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if request.method == 'POST':
        pilot_id = request.form['pilot_id']
        flight_id = request.form['flight_id']

        cursor.execute("UPDATE Flights SET pilot_id = ? WHERE id = ?", (pilot_id, flight_id))
        conn.commit()
        flash('Pilot assigned to flight successfully', 'success')

    cursor.execute("SELECT * FROM Users WHERE user_type = 'pilot'")
    pilots = cursor.fetchall()
    cursor.execute("SELECT * FROM Flights")
    flights = cursor.fetchall()
    conn.close()
    return render_template('assign.html', pilots=pilots, flights=flights)


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/admin_home')
def admin_home():
    return render_template('admin_home.html')

@app.route('/atcontrol')
def atcontrol():
    return render_template('atcontrol.html')

@app.route('/flights')
def flights():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Flights')
    flights = cursor.fetchall()
    conn.close()
    return render_template('flights.html', flights=flights)


if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True)
