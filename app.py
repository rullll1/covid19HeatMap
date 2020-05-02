from flask import Flask, request, jsonify, render_template
import json
import sqlite3


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('map.html')


@app.route('/data')
def send_data():
    with open('data.json') as f:
        data = json.load(f)
    return jsonify(data)


@app.route('/data/<string:country>')
def get_country_data(country):
    con = sqlite3.connect('data\data.db')
    cursor = con.cursor()
    query = "select * from countries where name=?"
    resp = cursor.execute(query, (country,))
    country_data = resp.fetchone()
    return {'country': country_data[1],
            'confirmed': country_data[2].split(', '),
            'delta_days': country_data[3].split(', '),
            'new_cases': country_data[4].split(', '),
            'total_deaths': country_data[5].split(', ')[-1],
            'total_cases': country_data[6]}


@app.route('/data/update_data', methods=['POST'])
def start_update():
    password = '1234'
    headers = request.headers
    if 'admin_key' not in headers:
        return {"error": "You are not admin"}, 401
    else:
        if headers['admin_key'] == password:
            from data import create_db
            return {'success': "updated the db!"}

        else:
            return {"error": "You are not admin"}, 401


app.run(port=5000)
