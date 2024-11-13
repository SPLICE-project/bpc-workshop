#!/usr/bin/env python3

from flask import Flask, request, render_template, Response
import json

app = Flask(__name__)

# Global variable to store temperatures
last_temperatures = {'C': 'N/A', 'F': 'N/A'}

@app.route('/data', methods=['POST'])
def data():
    global last_temperatures
    data = request.json
    print(data)
    if data:
        last_temperatures['C'] = data.get('temperatureC', 'N/A')
        last_temperatures['F'] = data.get('temperatureF', 'N/A')
    return 'Data received\n'

def generate_latest_temperature():
    global last_temperatures
    while True:
        # You could add logic here to only yield new data
        json_data = json.dumps(last_temperatures)
        yield f"data:{json_data}\n\n"

@app.route('/temperature_stream')
def temperature_stream():
    return Response(generate_latest_temperature(), mimetype='text/event-stream')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

