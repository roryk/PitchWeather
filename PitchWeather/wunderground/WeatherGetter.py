from urllib2 import urlopen, URLError
from WeatherContainer import WeatherContainer
import datetime
import sys
import yaml
import os

WEATHERHEADER = ['timeEST', 'tempF', 'dewF', 'humidity', 'pressure', 'visibility',
                 'windDir', 'windSpeed', 'gustSpeed', 'precip', 'events',
                 'conditions', 'windDirDeg', 'timeUTC']


class WeatherGetter(object):

    baseurl = "http://www.wunderground.com/history/airport"

    def __init__(self):
        self.csv = ""


    def getWeatherForDay(self, airport, year, month, day):
        if(self._getDayFromWunderground(airport, year, month, day)):
            return self._getWeatherObjects(airport)
        else:
            return None
        
    def _getDayFromWunderground(self, airport, year, month, day):
        """ downloads a single day of airport data, does not write it """
        # skip this silently if it isnt a valid day
        if not self._isValidDay(year, month, day):
            return False
        url = "/".join([self.baseurl, airport,
                       str(year), str(month), str(day),
                        "DailyHistory.html?format=1"])
        print url
        try:
            response = urlopen(url)
        except URLError:
            sys.stderr.write("Error opening %s, skipping." %(url))
            return False
        
        self.csv = response.read()
        self.csv = self.csv.replace('<br />', '')
        return True

    def _writeDay(self, airport, year, month, day):
        """ write a single day of airport weather to a file """
        fname = "_".join([airport, str(year), str(month), str(day)]) + ".csv"
        f = open(self.dirname + "/" + fname, "w")
        f.write(self.csv)

    def _dump(self):
        self.csv = ""

    def _isValidDay(self, year, month, day):
        """ returns True if this is a valid day, False otherwise """
        valid = True
        try:
            datetime.date(int(year), int(month), int(day))
        except ValueError:
            valid = False

        return valid

    def getWeatherForMonth(self, airport, year, month):
        """ gets and writes a month of daily airport weather data """
        weathers = []
        for day in xrange(1, 32):
            weather = self.getWeatherForDay(airport, year, month, day)
            if weather is None:
                continue
            else:
                weathers.append(weather)
        return weathers
                

    def getWeatherForYear(self, airport, year):
        """ gets and writes a year of daily airport weather data """
        weathers = []
        for month in xrange(1, 13):
            monthly = self.getWeatherForMonth(airport, year, month)
            weathers = weathers + monthly
        return weathers
    
    def _getWeatherObjects(self, airport):
        x = self.csv.split('\n')[2:]
        weatherObjects = []
        for line in x:
            if line == '':
                continue
            line = dict(zip(WEATHERHEADER, line.split(',')))
            weather = WeatherContainer(line)
            weather.airport = airport
            weatherObjects.append(weather)

        return weatherObjects

class StadiumWeatherGetter(WeatherGetter):
    """
    parses a yaml file with stadium information and uses it to download
    data from the nearest airport using wunderground
    """

    def __init__(self):
        self._read()

    def getWeatherForYearAtStadium(self, stadium, year):
        airport = stadium['airport']
        #yearly_weather = self.getWeatherForYear(airport, year)
        yearly_weather = self.getWeatherForMonth(airport, year, 2)
        for daily_weather in yearly_weather:
            for hourly_weather in daily_weather:
                hourly_weather.stadium = stadium['id']
        return yearly_weather

    def getWeatherForDayAtStadium(self, stadium, year, month, day):
        airport = stadium['airport']
        daily_weather = self.getWeatherForDay(airport, year, month, day)
        for hourly_weather in daily_weather:
            hourly_weather.stadium = stadium['id']
        return daily_weather
    
    def getStadiums(self):
        return self._stadiums
    
    def _read(self):
        this_dir, this_filename = os.path.split(__file__)
        parkfile = os.path.join(this_dir, "..", "data", "ballparks.yaml")
        f = open(parkfile, "r")
        self._stadiums =  yaml.load(f)
        self._stadiumIterator = iter(self._stadiums)
