from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db = SQLAlchemy(app)

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
        'pushback': 'Pushback approved',
        'taxi': 'Taxi to runway 32R, via taxiway Alpha, Bravo',
        'takeoff': 'Winds 320 at 10, runway 32R, cleared for takeoff',
        'requesting engine start': 'Engine start approved',
        'preflight checks complete': 'Cleared for pushback and engine start',
    },
    'Landing': {
        'ready for landing': 'Cleared to land runway 32R',
        'clear of the runway': 'Taxi to gate B7',
    },
    'Emergencies': {
        'emergency declaration': 'Roger your Mayday. What is your request?',
        'request landing': 'Emergency services are standing by.',
        'requesting assistance and instructions': 'I have cleared airspace for your emergency descent. Nearest suitable airport is 20 miles northwest. I will provide vectors for approach. Emergency services have been alerted. Confirm souls on board and fuel remaining.',
    },
    'Miscellaneous': {
        'requesting diversion': 'Cleared to alternate airport',
        'weather alert': 'Turn 270',
        'navigation system down': 'Turn right heading 180 for vectors',
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

# Route to handle sending messages from pilot or ATC
@app.route('/send_message/<role>', methods=['POST'])
def send_message(role):
    if role == 'Pilot':
        instruction = request.form['instruction']
        message = instruction
    else:
        message = request.form['message']
        # Check if the message is in the instruction map
        for category, instructions in instruction_map.items():
            if message in instructions:
                # If so, set the message to the corresponding response
                message = instructions[message]
                break
    new_message = Message(role=role, message=message)
    db.session.add(new_message)
    db.session.commit()
    return redirect(url_for('chat', role=role))

# Route to fetch messages for a specific role (ATC or pilot)
@app.route('/fetch_messages')
def fetch_messages():
    messages = Message.query.order_by(Message.timestamp).all()
    message_list = [{'role': msg.role, 'message': msg.message, 'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'id': msg.id, 'accepted': msg.accepted} for msg in messages]
    return jsonify(message_list)

# Route to accept a message
@app.route('/accept_message/<message_id>', methods=['POST'])
def accept_message(message_id):
    message = Message.query.get_or_404(message_id)
    message.accepted = True
    db.session.commit()
    return redirect(url_for('chat', role=message.role))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
