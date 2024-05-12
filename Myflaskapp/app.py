from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

instruction_map = {
    'Departure': {
    'pushback':'Pushback approved',
    'ready for pushback': 'Pushback approved',
    'ready to taxi': 'Taxi to runway 32R, via taxiway Alpha, Bravo',
    'taxi':'Taxi to runway 32R, via taxiway Alpha, Bravo',
    'ready for departure': 'Winds 320 at 10, runway 32R, cleared for takeoff',
    'departure':'Winds 320 at 10, runway 32R, cleared for takeoff',
    'takeoff':'Winds 320 at 10, runway 32R, cleared for takeoff',
    'requesting engine start': 'Engine start approved',
    'engine': 'Engine start approved',
    'preflight checks complete': 'Cleared for pushback and engine start',
    'check':'Cleared for pushback and engine start',
}
,
    'Landing': {
        'ready for landing': 'Cleared to land runway 32R',
        'landing': 'Cleared to land runway 32R',
        'runway':'Taxi to gate B7',
        'clear of the runway': 'Taxi to gate B7',
        
    },
    'Emergencies': {
        'mayday': 'Roger your Mayday. What is your request?',
        'request landing' :'Emergency services are standing by.'
        
    },
    'Miscellaneous': {
        'requesting diversion': 'Cleared to alternate airport',
        'diversion' : 'Cleared to alternate airport',
        'weather alert': 'Turn 270',
        'weather': 'Turn 270',
        'navigation system down': 'turn right heading 180 for vectors',
        
    }
}

chat_history = []

@socketio.on('send_message')
def handle_message(message_data):
    message = message_data['message'].lower()
    chat_type = message_data['chatType']
    
    instructions = []
    if chat_type in instruction_map:
        for keyword, instruction in instruction_map[chat_type].items():
            if keyword in message:
                instructions.append(instruction)
    
    new_message = {'role': 'Pilot', 'message': message_data['message']}
    chat_history.append(new_message)
    
    emit('receive_message', {'role': 'Pilot', 'message': message_data['message']})
    emit('receive_message', {'role': 'ATC', 'message': ', '.join(instructions) if instructions else 'No instruction found, try it in other way.'})

@app.route('/')
def index():
    return render_template('index.html', chat_history=chat_history)

if __name__ == '__main__':
    socketio.run(app, debug=True)
