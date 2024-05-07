from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    table_data = [
        ["A10023", "20:00-22:00", "READY"],
        ["A12233", "13:00-19:00", "NOT READY"],
        ["A45677", "12:00-3:00", "NOT READ"]
    ]
    return render_template('adminflight.html', table_data=table_data)

@app.route('/update', methods=['POST'])
def update():
    updated_data = request.get_json()  
    print("Updated Data:", updated_data)
    return "Success"

if __name__ == '__main__':
    app.run(debug=True)

