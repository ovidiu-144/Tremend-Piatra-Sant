import os
import sys


base_path = os.path.dirname(os.path.dirname(__file__))

if base_path not in sys.path:
    sys.path.append(base_path)

import pandas as pd
import numpy as np
from data.data_class.weatherData import *
from data.weather import get_area_weather

def parse_api(lat, long, start, end, events=None):
    weather_data = get_area_weather(lat, long, start, end)

    event_dates = set()
    if events:
        for event in events:
            if event.data_start:
                event_dates.add(str(event.data_start)[:10])

    data_list = []

    for area, weather_list in weather_data.items():
        for weather in weather_list:
            date_str = str(weather.date)[:10]
            data = pd.DataFrame({
                'ds': [weather.date],
                'temp': [np.mean([weather.temperature_min, weather.temperature_max])],
                'humidity': [weather.humidity],
                'precip': [weather.precipitation],
                'snow': [0.0],
                'windspeed': [weather.wind_speed],
                'preciptype_rain': [0.0],
                'preciptype_snow': [0.0],
                'is_event_day': [1.0 if date_str in event_dates else 0.0]
            })

            data['ds'] = pd.to_datetime(data['ds'])

            data_list.append(data)
        
    return data_list

if __name__ == "__main__":
    parse_api(45.6427, 25.5887, "2026-04-01", "2026-04-01")