from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = SQLAlchemy(app)
socketio = SocketIO(app)

basedir = os.path.abspath(os.path.dirname(__file__))

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_id = db.Column(db.String(10), unique=True, nullable=False)
    flight_number = db.Column(db.String(10), nullable=False)
    messages = db.relationship('Message', backref='flight', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(10), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    accepted = db.Column(db.Boolean, default=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    flight = db.relationship('Flight', backref=db.backref('messages', lazy=True))

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

flights = [
    {'flight_id': 'A001', 'flight_number': 'UA1234'},
    {'flight_id': 'A002', 'flight_number': 'AA5678'},
    {'flight_id': 'A003', 'flight_number': 'DL9012'}
]

@app.route('/')
def index():
    return render_template('index.html', flights=flights)

@app.route('/role/<flight_id>')
def role_selection(flight_id):
    return render_template('role_selection.html', flight_id=flight_id)

@app.route('/chat/<flight_id>/<role>')
def chat(flight_id, role):
    return render_template('chat.html', flight_id=flight_id, role=role)

@app.route('/fetch_messages/<flight_id>')
def fetch_messages_for_flight(flight_id):
    messages = Message.query.filter_by(flight_id=flight_id).order_by(Message.timestamp).all()
    return jsonify([{
        'id': msg.id,
        'role': msg.role,
        'message': msg.message,
        'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'accepted': msg.accepted
    } for msg in messages])
    
@socketio.on('send_message')
def send_message(data):
    role = data['role']
    message = data['message']
    flight_id = data['flight_id']

    print(f"Received message from {role}: {message} (Flight ID: {flight_id})")  # 添加日志

    new_message = Message(role=role, message=message, flight_id=flight_id)
    db.session.add(new_message)
    db.session.commit()

    socketio.emit('new_message', {
        'role': role,
        'message': message,
        'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'id': new_message.id,
        'accepted': new_message.accepted
    }, broadcast=True)
@socketio.on('accept_message')
def accept_message(message_id):
    message = Message.query.get_or_404(message_id)
    message.accepted = True
    db.session.commit()
    
    socketio.emit('message_accepted', {
        'id': message.id,
        'role': message.role,
        'message': message.message,
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'accepted': message.accepted
    }, broadcast=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
