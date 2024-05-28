from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Set a secret key for security
db = SQLAlchemy(app)
socketio = SocketIO(app)

# Define the Message model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(10), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    accepted = db.Column(db.Boolean, default=False)

# Instructions map for ATC responses
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

# Route to render the main chat page
@app.route('/')
def chat_home():
    return render_template('chat_home.html')

# Route to render the chat for a specific role (ATC or pilot)
@app.route('/chat/<role>')
def chat(role):
    messages = Message.query.order_by(Message.timestamp).all()
    return render_template('chat.html', role=role, messages=messages, instruction_map=instruction_map)

# Route to fetch messages
@app.route('/fetch_messages')
def fetch_messages():
    messages = Message.query.order_by(Message.timestamp).all()
    return jsonify([{
        'id': msg.id,
        'role': msg.role,
        'message': msg.message,
        'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'accepted': msg.accepted
    } for msg in messages])

# Route to handle sending messages from pilot or ATC
@socketio.on('send_message')
def send_message(data):
    role = data['role']
    if role == 'Pilot':
        instruction = data['instruction']
        message = instruction
    else:
        message = data['message']
        # Check if the message is in the instruction map
        for category, instructions in instruction_map.items():
            if message in instructions:
                # If so, set the message to the corresponding response
                message = instructions[message]
                break
    new_message = Message(role=role, message=message)
    db.session.add(new_message)
    db.session.commit()
    socketio.emit('new_message', {
        'role': role,
        'message': message,
        'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'id': new_message.id,
        'accepted': new_message.accepted
    }, broadcast=True)

# Route to accept a message
@socketio.on('accept_message')
def accept_message(message_id):
    message = Message.query.get_or_404(message_id)
    message.accepted = True
    db.session.commit()
    # Automatically send a response from ATC when a message is accepted
    response_message = None
    for category, instructions in instruction_map.items():
        if message.message in instructions:
            response_message = instructions[message.message]
            break
    if response_message:
        new_message = Message(role='ATC', message=response_message)
        db.session.add(new_message)
        db.session.commit()
        socketio.emit('new_message', {
            'role': 'ATC',
            'message': response_message,
            'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'id': new_message.id,
            'accepted': new_message.accepted
        }, broadcast=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
