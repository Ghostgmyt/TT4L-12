from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Function to create the database and tables
def create_database():
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()

    # Create Flight table
    cursor.execute('''CREATE TABLE IF NOT EXISTS flight (
                    id INTEGER PRIMARY KEY,
                    flight_number TEXT UNIQUE NOT NULL,
                    departure_time TEXT NOT NULL,
                    assigned_by TEXT NOT NULL,
                    pilot TEXT
                    )''')

    # Create Pilot table
    cursor.execute('''CREATE TABLE IF NOT EXISTS pilot (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                    )''')

    conn.commit()
    conn.close()

# Create the database and tables
create_database()

# Function to get flights from the database
def get_flights():
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM flight')
    flights_data = cursor.fetchall()

    flights = []
    for flight_data in flights_data:
        flights.append({
            'flight_number': flight_data[1],
            'departure_time': flight_data[2],
            'assigned_by': flight_data[3],
            'pilot': flight_data[4]
        })

    conn.close()
    return flights

# Function to insert a new row into the flight table
def insert_flight(flight_number, departure_time, assigned_by, pilot=None):
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO flight (flight_number, departure_time, assigned_by, pilot) VALUES (?, ?, ?, ?)',
                   (flight_number, departure_time, assigned_by, pilot))

    conn.commit()
    conn.close()

# Function to update flight's pilot in the database
def update_flight_pilot(flight_number, selected_pilot):
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE flight SET pilot = ? WHERE flight_number = ?', (selected_pilot, flight_number))

    conn.commit()
    conn.close()

# Function to add a new pilot to the database
def add_pilot(name):
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO pilot (name) VALUES (?)', (name,))

    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('admin.html')

@app.route('/pilots')
def pilots_page():
    flights = get_flights()
    pilots = ['P001', 'P002', 'P003', 'P004', 'P005']
    return render_template('pilots.html', flights=flights, pilots=pilots)

@app.route('/assign_pilot', methods=['POST'])
def assign_pilot():
    if request.method == 'POST':
        flight_number = request.form['flight_number']
        selected_pilot = request.form['selected_pilot']
        
        # Update the flight's pilot
        update_flight_pilot(flight_number, selected_pilot)
            
        # Send message to the selected pilot (you can implement this functionality)
        message = f'You have been assigned to flight {flight_number}.'
        # You can choose how to send the message, such as displaying on a web page or sending an email
        
    return redirect(url_for('pilots_page'))

@app.route('/flights')
def flights_page():
    return 'Welcome to admin page'

@app.route('/chat')
def chat_page():
    return 'Welcome to the Chat Page!'

if __name__ == '__main__':
    app.run(debug=True)
