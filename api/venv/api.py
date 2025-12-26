from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
import csv
from datetime import datetime
from datetime import date

app = Flask(__name__)
CORS(app)

API_KEY = '///////////'
url = 'https://www.carboninterface.com/api/v1/estimates'
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

@app.route("/api/fetch-electricity", methods=['GET'])
def fetch_electricity():
    attributes = request.args.getlist('attributes')
    payload = {
        "type": "electricity",
        "electricity_unit":attributes[0],
        "electricity_value": int(attributes[1]),
        "country": attributes[2],
        "state": attributes[3]
    }

    # Making the GET request
    response = requests.post(url, headers=headers, json=payload)

    # Checking the response status
    if response.status_code == 201:
        data_row = {"carbon_g":response.json()['data']['attributes']["carbon_g"],
                    "carbon_lb":response.json()['data']['attributes']["carbon_lb"],
                    "carbon_kg":response.json()['data']['attributes']["carbon_kg"],
                    "carbon_mt":response.json()['data']['attributes']["carbon_mt"],
                    "type":"electricity"}
        print(response.json())
        return jsonify(data_row)
    else:
        return jsonify({'error': f'Request failed with status {response.status_code}'}), response.status_code


@app.route("/api/fetch-flight", methods=['GET'])
def fetch_flight():
    attributes = request.args.getlist('attributes')
    roundTrip = request.args.get('roundTrip')
    departureAirport = request.args.get('departureAirport')
    destinationAirport = request.args.get('destinationAirport')

    legsList = []

    if roundTrip == "true":
        legsList = [{"departure_airport":departureAirport, "destination_airport":destinationAirport},
                    {"departure_airport":destinationAirport, "destination_airport":departureAirport}]
    else:
        legsList = [{"departure_airport":departureAirport, "destination_airport":destinationAirport}]
    print(legsList,"asdfasdf")
    print(attributes)
    payload = {
        "type": "flight",
        "passengers": int(attributes[0]),
        "legs": legsList,  # Pass the legs dictionary here
        "distance_unit": attributes[1]
    }

    # Making the GET request
    response = requests.post(url, headers=headers, json=payload)

    # Checking the response status
    if response.status_code == 201:
        data_row = {"carbon_g":response.json()['data']['attributes']["carbon_g"],
                    "carbon_lb":response.json()['data']['attributes']["carbon_lb"],
                    "carbon_kg":response.json()['data']['attributes']["carbon_kg"],
                    "carbon_mt":response.json()['data']['attributes']["carbon_mt"],
                    "type":"flight"}
        return jsonify(data_row)
    else:
        return jsonify({'error': f'Request failed with status {response.status_code}'}), response.status_code



@app.route("/api/fetch-fuel-combustion", methods=['GET'])
def fetch_fuel_combustion():
    attributes = request.args.getlist('attributes')
    payload = {
        "type": "fuel_combustion",
        "fuel_source_type": attributes[0],
        "fuel_source_unit": attributes[1],
        "fuel_source_value": attributes[2]
    }

    # Making the GET request
    response = requests.post(url, headers=headers, json=payload)

    # Checking the response status
    if response.status_code == 201:
        data_row = {"carbon_g":response.json()['data']['attributes']["carbon_g"],
                    "carbon_lb":response.json()['data']['attributes']["carbon_lb"],
                    "carbon_kg":response.json()['data']['attributes']["carbon_kg"],
                    "carbon_mt":response.json()['data']['attributes']["carbon_mt"],
                    "type":"fuel_combustion"}
        return jsonify(data_row)
    else:
        return jsonify({'error': f'Request failed with status {response.status_code}'}), response.status_code


@app.route("/api/fetch-shipping", methods=['GET'])
def fetch_shipping():
    attributes = request.args.getlist('attributes')
    payload = {
        "type": "shipping",
        "weight_unit": attributes[0],
        "weight_value": attributes[1],
        "distance_unit": attributes[2],
        "distance_value": attributes[3],
        "transport_method": attributes[4]
    }

    # Making the GET request
    response = requests.post(url, headers=headers, json=payload)

    # Checking the response status
    if response.status_code == 201:
        data_row = {"carbon_g":response.json()['data']['attributes']["carbon_g"],
                    "carbon_lb":response.json()['data']['attributes']["carbon_lb"],
                    "carbon_kg":response.json()['data']['attributes']["carbon_kg"],
                    "carbon_mt":response.json()['data']['attributes']["carbon_mt"],
                    "type":"shipping"}
        return jsonify(data_row)
    else:
        return jsonify({'error': f'Request failed with status {response.status_code}'}), response.status_code


@app.route("/api/fetch-vehicle", methods=['GET'])
def fetch_vehicle():
    attributes = request.args.getlist('attributes')
    vehicle_id = ''
    payload = {
        "type": "vehicle",
        "distance_unit": attributes[0],
        "distance_value": attributes[1],
        "vehicle_model_id": vehicle_id
    }

    # Making the GET request
    vehicle_make_response = requests.get("https://www.carboninterface.com/api/v1/vehicle_makes", headers=headers)

    vehicle_company_name = attributes[2].lower().strip()
    vehicle_id = ''

    for i in vehicle_make_response.json():
        if i['data']['attributes']['name'].lower() == vehicle_company_name.lower():
            vehicle_model_response = requests.get(f"https://www.carboninterface.com/api/v1/vehicle_makes/{i['data']['id']}/vehicle_models", headers=headers)

            vehicle_name = attributes[3].lower().strip()
            vehicle_year = attributes[4]

            for x in vehicle_model_response.json():
                if  vehicle_name.lower() in x['data']['attributes']['name'].lower() and int(x['data']['attributes']['year']) == int(vehicle_year):
                    vehicle_id = x['data']['id']
                    payload['vehicle_model_id'] = vehicle_id
                    print(vehicle_id)
                    break

    response = requests.post(url, headers=headers, json=payload)

    # Checking the response status
    if response.status_code == 201:
        data_row = data_row = {"carbon_g":response.json()['data']['attributes']["carbon_g"],
                    "carbon_lb":response.json()['data']['attributes']["carbon_lb"],
                    "carbon_kg":response.json()['data']['attributes']["carbon_kg"],
                    "carbon_mt":response.json()['data']['attributes']["carbon_mt"],
                    "type":"vehicle"}
        return jsonify(data_row)
    else:
        return jsonify({'error': f'Request failed with status {response.status_code}'}), response.status_code

@app.route('/append-data', methods=['POST'])
def append_data():
    data = request.json
    with open('data.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        today_date = datetime.today().strftime('%m/%d/%Y')
        writer.writerow([today_date, data['carbon_g'], data['carbon_lb'], data['carbon_kg'], data['carbon_mt'], data['type']])
    return jsonify({'message': 'Data appended successfully'}), 200

@app.route('/get-today-emissions', methods=['GET'])
def get_today_emissions():
    today = date.today().strftime('%m/%d/%Y')
    emissions_data = []

    with open('data.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == today:
                print({
                    'type': row[5],
                    'carbon_lb': float(row[2])
                })
                emissions_data.append({
                    'type': row[5],
                    'carbon_lb': float(row[2])
                })
    
    return jsonify(emissions_data)

@app.route('/api/history', methods=['GET'])
def get_history():
    results = []
    with open('data.csv', mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            results.append(row)
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
