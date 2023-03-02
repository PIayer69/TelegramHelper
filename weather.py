import requests
import datetime


class Weather:
    def __init__(self):
        API = "API"
        self.URL = "https://api.openweathermap.org"
        self.URL_WEATHER = self.URL + "/data/2.5/forecast"
        self.URL_GEO = self.URL + "/geo/1.0/direct"

        self.params = {
            "units": "metric",
            "lang": "pl",
            "appid": API,
        }

    def getGeo(self, city: str, country: str) -> dict:
        params = self.params
        params["q"] = f"{city},,{country}"
        r = requests.get(self.URL_GEO, params=params)
        data = r.json()[0]
        return {"lat": data["lat"], "lon": data["lon"]}

    def getWeather(self, city: str, country: str) -> dict:
        geo = self.getGeo(city, country)
        params = {**self.params, **geo}
        r = requests.get(self.URL_WEATHER, params=params)
        return r.json()
    
    def loadWeather(self, weatherData):
        self.weatherData = weatherData
    
    @staticmethod
    def prepareWeather(weatherData: dict) -> str:
        date = datetime.datetime.fromtimestamp(weather['dt']).strftime("%d.%m.%Y %H:%M")
        text = f"""
                {date}\n
                Temperatura: {weather['main']['temp']}°C\n
                Odczuwalna: {weather['main']['feels_like']}°C\n
                Widoczność: {weather['visibility']}km\n
                Opis: {weather['weather'][0]['description']}\n
                """
        if 'wind' in weather.keys():
            text += f"Prędkość wiatru: {weather['wind']['speed']}km/h\n"
        if 'rain' in weather.keys():
            text += f"Opady deszczu: {weather['rain']['3h']}mm\n"
        if 'snow' in weather.keys():
            text += f"Opady śniegu: {weather['snow']['3h']}mm\n"
                
            

if __name__ == "__main__":
    import json
    
    with open('w', 'r') as f:
        data = json.loads(f.read())
        
    w = Weather()
    w.retrieveWeather(data['list'])