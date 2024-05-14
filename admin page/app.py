from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

table_data = [
    ["AIRASIA", "A10023", "20:00-22:00", "READY"],
    ["AIRASIA", "A12233", "13:00-19:00", "NOT READY"],
    ["AIRASIA", "A45677", "12:00-3:00", "NOT READY"],
    ["AIRASIA", "A23456", "14:00-15:00", "READY"],
    ["AIRASIA", "A87654", "9:00-13:00", "NOT READY"],
    ["AIRASIA", "A45687", "1:00-4:00", "NOT READY"],
    ["AIRASIA", "A96753", "13:00-16:00", "NOT READY"],
    ["AIRASIA", "A16662", "18:00-20:00", "READY"],
    ["AIRASIA", "A09876", "7:00-10:00", "READY"]
]

@app.route('/')
def index():
    return render_template('adminflight.html', table_data=table_data)

@app.route('/update', methods=['POST'])
def update():
    global table_data  
    updated_data = request.get_json()  
    table_data = updated_data 
    print("Updated Data:", table_data)
    return "Success"

if __name__ == '__main__':
    app.run(debug=True)

