import os
import sys
import requests
import pandas as pd

base_path = os.path.dirname(os.path.dirname(__file__))

if base_path not in sys.path:
    sys.path.append(base_path)

from data.data_class.weatherData import WeatherData

def get_daily_weather(lat, lon, start_date, end_date):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": [
            "temperature_2m_max", 
            "temperature_2m_min", 
            "precipitation_sum",
            "snowfall_sum",
            "weathercode",
            "relative_humidity_2m_max",
            "windspeed_10m_max"         
        ],
        "timezone": "auto"
    }
    
    response = requests.get(url, params=params)
    weatherList = []

    if response.status_code == 200:
        data = response.json()
        df_daily = pd.DataFrame(data['daily'])
        
        for index, row in df_daily.iterrows():
            # Cream obiectul WeatherData cu datele mapate corect
            w_data = WeatherData(
                date=row['time'],
                temperature=(row['temperature_2m_max'] + row['temperature_2m_min']) / 2, # Medie
                temperature_min=row['temperature_2m_min'],
                temperature_max=row['temperature_2m_max'],
                precipitation=row['precipitation_sum'],
                snowfall=row['snowfall_sum'],
                humidity=row['relative_humidity_2m_max'],
                wind_speed=row['windspeed_10m_max'],
                weather_code=get_weather_description(row['weathercode']),
                date_str=str(row['time'])
            )
            # Adaugam campuri extra daca clasa WeatherData permite, 
            # pentru a nu pierde informatia despre precipitatii (critica pt triaj)            
            weatherList.append(w_data)
        return weatherList
    return None

def get_weather_description(code):
    wmo_codes = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        66: "Light freezing rain", 67: "Heavy freezing rain",
        71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        85: "Slight snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
    }
    return wmo_codes.get(code, "Unknown")

def get_area_weather(lat, lon, start_date, end_date):

    offset = 0.09  # aprox 10km
    locations = [
        {"name": "Centru", "lat": lat, "lon": lon},
        {"name": "Nord", "lat": lat + offset, "lon": lon},
        {"name": "Sud", "lat": lat - offset, "lon": lon},
        {"name": "Est", "lat": lat, "lon": lon + offset},
        {"name": "Vest", "lat": lat, "lon": lon - offset}
    ]
    
    all_area_data = {}
    for loc in locations:
        # Refolosim functia ta existenta pentru fiecare punct
        all_area_data[loc['name']] = get_daily_weather(loc['lat'], loc['lon'], start_date, end_date)
    
    return all_area_data


# Exemplu de utilizare pentru Spitalul din Brasov (folosind coordonatele tale)
# df_vreme = get_daily_weather(45.6427, 25.5887, "2026-04-01", "2026-04-02")
# print(df_vreme)
# for weather in df_vreme:
#     print(weather)

# print("\n--- Vreme pe zone ---\n")

# df_area = get_area_weather(45.6427, 25.5887, "2026-04-01", "2026-04-05")
# for area, weather_list in df_area.items():
#     print(f"Zona: {area}")
#     for weather in weather_list:
#         print(weather)