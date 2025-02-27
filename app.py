from flask import Flask, request, jsonify, render_template
import requests
import threading
from datetime import datetime, timedelta
import time
import json
import pytz


app = Flask(__name__)

# KONFIGURATION
ip = "192.168.1.56" 
# ip = "192.168.1.100"

room_data = {
    'Obyvak': {
                # 'sensor_id': "26D6B514020000F3",
               'sensor_id': "281759D409000027",               
            #    'relay': '8',
               'relay': '1_01',
               'target_temp': 24.0,
               'dayTempTarget': 24.0,
               'dayModeTimeStart': "07:30",
               'dayModeTimeEnd': "20:30",
               'nightTempTarget': 19.0,
               'current_temp': 20.0,
               'mode': 'dayMode',
               'heating_on': True,
               'monitoring': True},
    # 'Obyvak-2': {'sensor_id': "26D6B514020000F3",
    #         #    'sensor_id': "281759D409000027",               
    #            'relay': '7',
    #         #    'relay': '1_01',
    #            'target_temp': 24.0,
    #            'dayTempTarget': 24.0,
    #            'dayModeTimeStart': "07:30",
    #            'dayModeTimeEnd': "20:30",
    #            'nightTempTarget': 19.0,
    #            'current_temp': 20.0,
    #            'mode': 'dayMode',
    #            'heating_on': True,
    #            'monitoring': True},
    'Chodba': {
                # 'sensor_id': "2627F5380200003D",
                 'sensor_id': "28AB019F0D00001C",
                #  'relay': '3',
                 'relay': '1_02',
                 'target_temp': 24.0,
                 'dayTempTarget': 24.0,
                 'dayModeTimeStart': "07:30",
                 'dayModeTimeEnd': "20:30",
                 'nightTempTarget': 19.0,
                 'current_temp': 20.0,
                 'mode': 'dayMode',
                 'heating_on': True,
                 'monitoring': False},
    'Ložnice': {
                #  'sensor_id': "26C5243902000066",
                'sensor_id': "284411D609000080",
                #  'relay': '6',
                 'relay': '1_03',
                 'target_temp': 24.0,
                 'dayTempTarget': 24.0,
                 'dayModeTimeStart': "20:30",
                 'dayModeTimeEnd': "07:30",
                 'nightTempTarget': 19.0,
                 'current_temp': 20.0,
                 'mode': 'dayMode',
                 'heating_on': True,
                 'monitoring': True},  
}




# def get_room_temperature(sensor_id):
#     try:
#         response = requests.get(f"http://{ip}/rest/sensor/{sensor_id}")
#         return float(response.json()["temp"])
#     except Exception as e:
#         print(f"Error: {e}")
#         return None
def get_room_temperature(sensor_id):
    try:
        response = requests.get(f"http://{ip}/json/sensor/{sensor_id}")
        return float(response.json()["value"])
    except Exception as e:
        print(f"Error: {e}")
        return None


# def heat_on(relay):
#     url = f"http://{ip}/json/relay/" + relay;
#     return requests.post(url, '{"value":"1"}')
def heat_on(relay):
    url = f"http://{ip}/json/ro/{relay}"
    return requests.post(url, '{"value":"1"}')

# def heat_off(relay):
#     url = f"http://{ip}/json//relay/" + relay;
#     return requests.post(url, '{"value":"0"}')

def heat_off(relay):
    url = f"http://{ip}/json/ro/{relay}"
    return requests.post(url, '{"value":"0"}')


# Endpoint pro získání aktualni teploty, osetrit chybu pri neexistujicim pokoji
@app.route('/room/<room_id>/temperature', methods=['GET'])
def getTemperature(room_id):
    room = room_data.get(room_id)
    temp = get_room_temperature(room['sensor_id'])
    if temp is not None:
        return jsonify({'temperature': temp})
    return jsonify({'error': 'Could not fetch temperature'}), 500



# Endpoint pro ziskani aktualni cilove teploty
@app.route('/room/<room_id>/get_target_temperature', methods=['GET'])
def get_target_temperature(room_id):
    room = room_data.get(room_id)
    return jsonify({'targetTemp': room['target_temp']})



# Endpoint pro nastaveni cilove teploty
@app.route('/room/<room_id>/set_target_temperature', methods=['POST'])
def set_target_temperature(room_id):
    global room_data
    data = request.json
    room = room_data.get(room_id)
    room['mode'] = get_mode(room_id)
    if 'targetTemp' in data:
        if room['mode'] == "dayMode":
            room['dayTempTarget'] = float(data['targetTemp'])
        else:
            room['nightTempTarget'] = float(data['targetTemp'])
        room['target_temp'] = float(data['targetTemp'])
        return jsonify({'status': 'Target temperature updated', 'targetTemp': room['target_temp']})
    return jsonify({'error': 'Invalid data'}), 400



# Prevod casu z forumulare na sekundy
def time_to_seconds(time_str):
    hours, minutes = map(int, time_str.split(":"))
    return hours * 3600 + minutes * 60

# Jaky rezim aktualne -> teplota
def get_mode(room_id):
    room = room_data[room_id]
    dayModeStartTimeSec = time_to_seconds(room['dayModeTimeStart'])
    dayModeEndTimeSec = time_to_seconds(room['dayModeTimeEnd'])
    tz = pytz.timezone("Europe/Prague")  
    now_seconds = datetime.now(tz).hour * 3600 + datetime.now().minute * 60

    # Standardní případ (denní režim je mezi startem a endem)
    if dayModeStartTimeSec < dayModeEndTimeSec:
        if dayModeStartTimeSec <= now_seconds < dayModeEndTimeSec:
            return "dayMode"
        else:
            return "nightMode"

    # Noční režim přes půlnoc (např. 22:00 - 06:00)
    else:
        if now_seconds >= dayModeStartTimeSec or now_seconds < dayModeEndTimeSec:
            return "dayMode"
        else:
            return "nightMode"




# REZIMY
# Denni rezim
# Endpoint pro nastaveni denniho rezimu
@app.route('/room/<room_id>/set_day_mode', methods=['POST'])
def set_day_mode(room_id):
    global room_data
    data = request.json
    room = room_data.get(room_id)
    if all(k in data for k in ['dayTempTarget', 'dayModeTimeStart', 'dayModeTimeEnd']):
        room['dayTempTarget'] = float(data['dayTempTarget'])
        room['dayModeTimeStart'] = data['dayModeTimeStart']
        room['dayModeTimeEnd'] = data['dayModeTimeEnd']
        return jsonify({'status': 'DayMode target temp updated',
                        'targetDayTemp': room['dayTempTarget'],
                        'dayModeStart': room['dayModeTimeStart'],
                        'dayModeEnd': room['dayModeTimeEnd']})
    return jsonify({'error': 'Invalid data'}), 400

# Nocni rezim
# Endpoint pro nastaveni nocniho rezimu
@app.route('/room/<room_id>/set_night_mode', methods=['POST'])
def set_night_mode(room_id):
    global room_data    
    data = request.json
    room = room_data.get(room_id)
    # if all(k in data for k in ['nightTempTarget', 'nightModeTimeStart', 'nightModeTimeEnd']):
    #     nightTempTarget = float(data['nightTempTarget'])
        # nightModeTimeStart = data['nightModeTimeStart']
        # nightModeTimeEnd = data['nightModeTimeEnd']
        # return jsonify({'status': 'DayMode target temp updated', 'targetNightTemp': nightTempTarget, 'nightModeStart': nightModeTimeStart, 'nightModeEnd': nightModeTimeEnd})
    if 'nightTempTarget' in data:
        room['nightTempTarget'] = float(data['nightTempTarget'])
        return jsonify({'status': 'DayMode target temp updated',
                        'targetNightTemp': room['nightTempTarget']})
    return jsonify({'error': 'Invalid data'}), 400



# Update 'monitoring' podle toggle switch pokoje
@app.route('/room/<room_id>/update_monitoring', methods=['POST'])
def update_monitoring(room_id):
    global room_data
    data = request.json
    room = room_data.get(room_id)
    
    if room:
        room['monitoring'] = data['monitoring']
        return jsonify({"status": "success", "monitoring": room['monitoring']})
    else:
        return jsonify({"status": "error", "message": "Room not found"}), 404

        
@app.route('/monitoring/<room_id>')
def monitoring(room_id):
    room = room_data.get(room_id)
    if room:
        return jsonify({"status": "success", "monitoring": room['monitoring']})
    else:
        return jsonify({"status": "error", "message": "Room not found"}), 404
    
    
            
# Ziskani teplot z pokoju na hlavni stranku
@app.route('/all_temperatures_heating_mode')
def all_temperatures_heating_mode():
    temperatures_heating_mode = {
        room_id: {
            "current_temp": data["current_temp"],
            "heating_on": data["heating_on"],
            "mode": data["mode"],
            'monitoring': data['monitoring']
        }
        for room_id, data in room_data.items()
    }
    return jsonify(temperatures_heating_mode)



# Sledovani teploty v pokoji, topeni zapnuto/vypnuto
def monitor_temperature(room_id):
    while True:
        room = room_data[room_id]
        sensor_id = room['sensor_id']
        relay = room['relay']
        current_temp = float(get_room_temperature(sensor_id))
        room['current_temp'] = current_temp
        room['mode'] = get_mode(room_id)
        
        if room['mode'] == "dayMode":
            room['target_temp'] = room['dayTempTarget']
        else:
            room['target_temp'] = room['nightTempTarget']
        
        target_temp = room['target_temp']

        # print(room)
        if current_temp is not None:
            if room['monitoring']:
                if current_temp < target_temp:
                    heat_on(relay)
                    room['heating_on'] = True
                else:
                    heat_off(relay)
                    room['heating_on'] = False
            else:
                heat_off(relay)
                room['heating_on'] = False
        time.sleep(6)


def start_monitoring_all_rooms():
    # Spustí monitorování pro všechny pokoje v room_data v samostatných vláknech
    for room_id in room_data.keys():
        threading.Thread(target=monitor_temperature, args=(room_id,), daemon=True).start()

start_monitoring_all_rooms()



# Webová stránka
@app.route('/room/<room_id>')
def room1(room_id):
    room = room_data.get(room_id)
    target_temp = room['target_temp']
    if room is None:
        return "Room not found", 404
    else:
        print("Accessed room1")
    current_temp = get_room_temperature(room['sensor_id'])
    return render_template(
        'room_page.html',
        room_id=room_id,
        room=room,
        current_temp=current_temp,
        target_temp=target_temp,
        dayTempTarget = room['dayTempTarget'],
        dayModeTimeStart = room['dayModeTimeStart'],
        dayModeTimeEnd = room['dayModeTimeEnd'],
        nightTempTarget = room['nightTempTarget'],
        monitoring = room['monitoring'])


@app.route('/')
def index():
    return render_template('mainpage.html',
                           room_data=room_data)


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0", debug=False)