import requests
import datetime
import random

greetings = ["Hejka", "Dzień dobry", "Cześć", "Hejo", "Pobudka"]


class Weather:
    def __init__(self, API):
        self.URL = "https://api.openweathermap.org"
        self.URL_FORECAST = self.URL + "/data/2.5/forecast"
        self.URL_WEATHER = self.URL + "/data/2.5/weather"
        self.URL_GEO = self.URL + "/geo/1.0/direct"

        self.params = {
            "units": "metric",
            "lang": "pl",
            "appid": API,
        }

    def getGeo(self, city: str, country: str) -> dict:
        # Takes city and country as args, returns longitude and latitude
        # OpenWeather API needs coordinates to return weather info
        params = self.params
        params["q"] = f"{city},,{country}"
        r = requests.get(self.URL_GEO, params=params)
        data = r.json()[0]
        return {"lat": data["lat"], "lon": data["lon"]}

    def getForecast(self, city: str, country: str) -> dict:
        # Takes city and country as argument, calls OpenWeather API and
        # returns list of forecast for 5 days forward
        self.lprint(f"Getting forecast for {city}...")
        geo = self.getGeo(city, country)
        params = {**self.params, **geo}
        r = requests.get(self.URL_FORECAST, params=params)
        return r.json()["list"]

    def getCurrentWeather(self, city: str, country: str) -> dict:
        # Takes city and country as argument, calls OpenWeather API and
        # returns useful data in string
        self.lprint(f"Getting current weather for {city}...")
        geo = self.getGeo(city, country)
        params = {**self.params, **geo}
        r = requests.get(self.URL_WEATHER, params=params)
        return self.prepareWeather(r.json(), city)

    def prepareForecast(self, forecastArray: list, city: str) -> str:
        forecastData = self.prepareForecastData(forecastArray)
        text = f"""
Pogoda - {city} - {forecastData['dt']}
Temperatura: {forecastData['temp']['min']}°C - {forecastData['temp']['max']}°C
Wiatr: {forecastData['wind']['min']}km/h - {forecastData['wind']['max']}km/h
Zachmurzenie: {"duże" if forecastData['clouds'] > 75
                else "średnie" if forecastData['clouds'] > 50
                else "małe" if forecastData['clouds'] > 25
                else "bardzo małe" if forecastData['clouds'] > 0
                else "bezchmurnie"}
{f"Deszcz: {forecastData['rain']}" if len(forecastData['rain'].keys()) else ""}
{f"Śnieg: {forecastData['snow']}" if len(forecastData['snow'].keys()) else ""}"""
        return text

    def prepareGreetingForecast(self, forecastArray: list, jobData: dict) -> str:
        forecastData = self.prepareForecastData(forecastArray)
        hour = datetime.datetime.now().hour
        text = f"{random.choice(greetings)} @{jobData['username']}\!\n"
        text += f"""
Pogoda na dzisiaj
Temperatura w granicach `{forecastData['temp']['min']}°C - {forecastData['temp']['max']}°C`
Będzie nam towarzyszył {'silny' if forecastData['wind']['max'] > 5 else 'słaby'} wiatr `{forecastData['wind']['min']}km/h - {forecastData['wind']['max']}km/h`
{"Bardzo zachmurzone" if forecastData['clouds'] > 75
else "Średnio zachmurzone" if forecastData['clouds'] > 50
else "Mało zachmurzone" if forecastData['clouds'] > 25
else "Bardzo mało zachmurzone" if forecastData['clouds'] > 0
else "Bezchmurne"} niebo
{f"Deszcz w godzinach: {' '.join([str(h) for h in forecastData['rain']['hour']])}" if len(forecastData["rain"]["hour"]) else ''}
{f"Śnieg w godzinach: {' '.join([str(h) for h in forecastData['snow']['hour']])}" if len(forecastData["snow"]["hour"]) else ''}"""
        return text

    @staticmethod
    def findForecastByDay(forecastData: list, day: int) -> list:
        # Function that returns forecasts only for specified day
        return [
            forecast
            for forecast in forecastData
            if datetime.datetime.fromtimestamp(forecast["dt"]).day == day
        ]

    @staticmethod
    def prepareForecastData(forecastArray: list) -> str:
        # Function that takes forecastArray and city as argument
        # and returns dictionary with useful data
        temperatures = [f["main"]["temp"] for f in forecastArray]
        wind = [f["wind"]["speed"] for f in forecastArray]
        clouds = [f["clouds"]["all"] for f in forecastArray if "clouds" in f.keys()]
        rain = {
            "hour": [
                datetime.datetime.fromtimestamp(f["dt"]).hour
                for f in forecastArray
                if "rain" in f.keys()
            ],
            "volume": sum(
                [f["rain"]["3h"] for f in forecastArray if "rain" in f.keys()]
            ),
        }
        snow = {
            "hour": [
                datetime.datetime.fromtimestamp(f["dt"]).hour
                for f in forecastArray
                if "snow" in f.keys()
            ],
            "volume": sum(
                [f["snow"]["3h"] for f in forecastArray if "snow" in f.keys()]
            ),
        }

        forecastData = {
            "dt": datetime.date.fromtimestamp(forecastArray[0]["dt"]),
            "temp": {"min": min(temperatures), "max": max(temperatures)},
            "wind": {
                "max": max(wind),
                "min": min(wind),
                "avg": round(sum(wind) / len(wind), 2),
            },
            "clouds": sum(clouds) / len(clouds),
            "rain": rain,
            "snow": snow,
        }
        return forecastData

    @staticmethod
    def prepareWeather(weather: dict, city: str) -> str:
        text = f"""
Pogoda - {city} - {datetime.datetime.fromtimestamp(weather["dt"])}
Temperatura: {weather['main']['temp']}°C | {weather['main']['feels_like']}°C
Widoczność: {weather['visibility']/1000}km
Opis: {weather['weather'][0]['description']}
"""

        if "wind" in weather.keys():
            text += f"Prędkość wiatru: {weather['wind']['speed']}km/h\n"
        if "rain" in weather.keys():
            text += f"Opady deszczu: {weather['rain']['3h']}mm\n"
        if "snow" in weather.keys():
            text += f"Opady śniegu: {weather['snow']['3h']}mm\n"
        return text
    
    @staticmethod
    def lprint(text):
        print(f"{datetime.datetime.now()}: {text}")


if __name__ == "__main__":
    w = Weather()
    forecastData = w.getForecast("Krakow", "PL")
    forecastDay = w.findForecastByDay(forecastData, 5)
    forecast = w.prepareForecast(forecastDay, "Krakow")
    # print(forecast)
    # w.analiseForecast(forecastDay)
