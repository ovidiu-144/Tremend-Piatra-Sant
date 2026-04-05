class WeatherData:
    def __init__(self, date, temperature, temperature_min, temperature_max, precipitation, snowfall, humidity, wind_speed, weather_code, date_str):
        self.date = date
        self.temperature = temperature
        self.temperature_min = temperature_min
        self.temperature_max = temperature_max
        self.precipitation = precipitation
        self.snowfall = snowfall
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.weather_code = weather_code
        self.date_str = date_str
    def __str__(self):
        return f"Date: {self.date_str}, Temp: {self.temperature}°C, Min: {self.temperature_min}°C, Max: {self.temperature_max}°C, Precipitation: {self.precipitation}mm, Snowfall: {self.snowfall}cm, Humidity: {self.humidity}%, Wind Speed: {self.wind_speed}km/h, Weather Code: {self.weather_code}"