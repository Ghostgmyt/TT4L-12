from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('admin.html')

@app.route('/pilots')
def pilots():
    flights = []
    for i in range(1, 11):
        flight_data = {
            "flight_number": f"FL00{i}",
            "departure_time": f"2024-06-01 {10 + i}:00",  
            "assigned_by": f"Admin {i}"
        }
        flights.append(flight_data)

    admins = ["Admin 1", "Admin 2"]

    pilots = ["P001", "P002", "P003", "P004", "P005"]

    return render_template('pilots.html', flights=flights, admins=admins, pilots=pilots)

@app.route('/flights')
def flights():
    return 'Welcome to the Flights Page!'

@app.route('/chat')
def chat():
    return 'Welcome to the Chat Page!'

if __name__ == '__main__':
    app.run(debug=True)
