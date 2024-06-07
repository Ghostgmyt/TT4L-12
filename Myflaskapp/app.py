from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
socketio = SocketIO(app)

DB_FILE = 'chat.db'

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

@app.route('/')
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

if __name__ == '__main__':
    socketio.run(app, debug=True)
