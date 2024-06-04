from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('pilotshome.html')

@app.route('/duty_roster')
def duty_roster():
    return render_template('duty_roster.html')

@app.route('/chat')
def chat():
    return 'Welcome to the Chat Page!'

# Define the duty_roster table model
class DutyRoster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pilot = db.Column(db.String(100))

# Define the Flight model (you may already have this defined)
class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(100))
    departure_time = db.Column(db.String(100))
    assigned_by = db.Column(db.String(100))
    pilot = db.Column(db.String(100))

# This route handles both GET and POST requests for the flight information
@app.route('/flights', methods=['GET', 'POST'])
def flights():
    if request.method == 'POST':
        with app.app_context():
            flight_id = request.form['flight_id']
            assigned_by = request.form['assigned_by']
            pilot = request.form['pilot']
            
            # Update the Flight record with assigned_by and pilot information
            flight = Flight.query.get(flight_id)
            flight.assigned_by = assigned_by
            flight.pilot = pilot
            db.session.commit()
            
            # Update the DutyRoster table with the new pilot information
            duty_roster_entry = DutyRoster(pilot=pilot)
            db.session.add(duty_roster_entry)
            db.session.commit()

    # Retrieve flights and admins (for select dropdowns)
    flights = Flight.query.all()
    admins = ['Admin1', 'Admin2', 'Admin3']  # Replace with actual admin names
    pilots = ['Pilot1', 'Pilot2', 'Pilot3']  # Replace with actual pilot names
    return render_template('flights.html', flights=flights, admins=admins, pilots=pilots)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)






