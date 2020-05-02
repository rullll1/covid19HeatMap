import pandas as pd
import datetime
import geopandas as gpd
import numpy as np
from urllib.error import HTTPError


def days_plague_in_country(country, current_date):
    delta = datetime.datetime.strptime(start_per_country[country], '%Y-%m-%d')
    n_days = (datetime.datetime.strptime(
        current_date, '%Y-%m-%d') - delta).days
    return n_days


last_update = '01-21-2020'
last_update_date = datetime.datetime.strptime(last_update, '%m-%d-%Y')

con = []
for i in range((datetime.datetime.today().date() - last_update_date.date()).days):
    date = (last_update_date + datetime.timedelta(days=i + 1)
            ).strftime("%m-%d-%Y")
    print(date)
    try:
        df = pd.read_csv(
            f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{date}.csv')
    except HTTPError:
        continue
    real_date = date.split('-')
    df['real_date'] = real_date[2] + '-' + real_date[0] + '-'+real_date[1]
    df.rename(columns={'Country/Region': 'Country',
                       'Country_Region': 'Country'}, inplace=True)
    con.append(df)

df = pd.concat(con)
df['Country'] = df['Country'].str.strip()
start_per_country = df.groupby(['Country'])['real_date'].min()
df['delta_days'] = df[['Country', 'real_date']].apply(
    lambda row: days_plague_in_country(row['Country'], row['real_date']), axis=1)

df.sort_values(by=['Country', 'real_date'], inplace=True)
df['new_cases'] = df.groupby('Country')['Confirmed'].diff(1)
df.fillna({'new_cases': 0}, inplace=True)
data_to_join = df.groupby('Country')[
    'Confirmed', 'new_cases', 'Deaths', 'delta_days'].agg(lambda x: str(list(x))[1:-1])

gdf = gpd.read_file(r'D:\Myprojects\flask_udemy\data\data.json')
gdf = gdf[['NAME', 'pop', 'geometry']]
gdf = gdf.join(df.groupby('Country')['Confirmed'].max(), on='NAME')
gdf.rename(columns={'Confirmed': 'totalCases'}, inplace=True)
gdf = gdf.join(data_to_join, on='NAME')
gdf['densCovid'] = gdf['totalCases'] / gdf['pop']
gdf['per'] = pd.qcut(gdf['densCovid'], 5, labels=[1, 2, 3, 4, 5]).astype(float)
gdf.fillna({'per': gdf['per'].mean(),
            'densCovid': gdf['densCovid'].mean(),
            'delta_days': gdf['delta_days'][0],
            'Confirmed': gdf['Confirmed'][0],
            'new_cases': gdf['new_cases'][0],
            'Deaths': gdf['Deaths'][0],
            'totalCases': gdf['totalCases'].mean(),
            'pop': gdf['pop'].mean()}, inplace=True)

open(r'D:\Myprojects\flask_udemy\data\data.json', 'w').write(gdf.to_json())
