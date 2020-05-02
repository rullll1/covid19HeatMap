import sqlite3
import json
import os
# import update_data

table_path = 'data/data.db'
geojson_data = 'data/data.json'
os.remove(table_path)

con = sqlite3.connect(table_path)

cursor = con.cursor()

create_table = "CREATE TABLE COUNTRIES (id INTEGER PRIMARY KEY, name text, confirmed_per_day text, delta_days text, new_cases text, deaths int, total_cases int)"
cursor.execute(create_table)

with open(geojson_data) as f:
    data = json.load(f)

for i in data['features']:
    prop = i['properties']
    name = prop['NAME']
    confirmed_per_day = prop['Confirmed']
    delta_days = prop['delta_days']
    new_cases = prop['new_cases']
    deaths = prop['Deaths']
    total_cases = prop['totalCases']

    query = "INSERT INTO COUNTRIES VALUES (NULL, ?, ?, ?, ?, ?, ?)"
    print(i['id'])
    cursor.execute(query, (name, confirmed_per_day,
                           delta_days, new_cases, deaths, total_cases))
con.commit()
con.close()
