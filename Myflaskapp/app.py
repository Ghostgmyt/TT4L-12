from flask import Flask, render_template

app = Flask(__name__)

# Extended communications breakdown by phase
communications = {
    'flight_departure': {
        'pushback': [
            {"role": "Pilot", "message": "Ground, AirAsia 123 at gate B7, ready for pushback."},
            {"role": "ATC", "message": "AirAsia 123, pushback approved."},
        ],
        'taxi': [
            {"role": "Pilot", "message": "AirAsia 123 ready to taxi."},
            {"role": "ATC", "message": "AirAsia 123, taxi to runway 32R, via taxiway Alpha, Bravo."},
        ],
        'takeoff': [
            {"role": "Pilot", "message": "Tower, AirAsia 123 at runway 32R, ready for departure."},
            {"role": "ATC", "message": "AirAsia 123, winds 320 at 10, runway 32R, cleared for takeoff."},
        ]
    },
    'flight_landing': {
        'approach': [
            {"role": "Pilot", "message": "Approach, AirAsia 123, descending through 10,000 feet."},
            {"role": "ATC", "message": "AirAsia 123, descend to 3,000 feet for runway 32R."},
        ],
        'landing': [
            {"role": "Pilot", "message": "Tower, AirAsia 123, ready for landing."},
            {"role": "ATC", "message": "AirAsia 123, cleared to land runway 32R."},
        ],
        'taxi_to_gate': [
            {"role": "Pilot", "message": "Tower, AirAsia 123, clear of the runway."},
            {"role": "ATC", "message": "AirAsia 123, taxi to gate B7."},
        ]
    },
    'emergencies': {
        'mayday': [
            {"role": "Pilot", "message": "Mayday, Mayday, Mayday, AirAsia AK123, engine failure."},
            {"role": "ATC", "message": "AirAsia AK123, roger your Mayday. What is your request?"},
        ],
        'emergency_landing': [
            {"role": "Pilot", "message": "Request immediate return to Kuala Lumpur."},
            {"role": "ATC", "message": "Cleared direct to runway 32R, descend to 10,000 feet."},
        ]
    },
    'miscellaneous': {
        'traffic_advisories': [
            {"role": "ATC", "message": "Traffic at your 3 o'clock."},
            {"role": "Pilot", "message": "Looking for traffic."},
        ],
        'weather_updates': [
            {"role": "ATC", "message": "Weather alert, turn 270."},
            {"role": "Pilot", "message": "Turning 270."},
        ]
    }
}

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/communications/<category>")
def show_category(category):
    subcategories = communications.get(category, {})
    return render_template('category.html', category=category, subcategories=subcategories)

@app.route("/communications/<category>/<subcategory>")
def show_subcategory(category, subcategory):
    messages = communications.get(category, {}).get(subcategory, [])
    return render_template('subcategory.html', category=category, subcategory=subcategory, messages=messages)

if __name__ == '__main__':
    app.run(debug=True)

