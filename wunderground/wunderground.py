from urllib2 import urlopen, URLError
import os
import datetime
import sys

class WeatherGetter(object):

    baseurl = "http://www.wunderground.com/history/airport"

    def __init__(self, dirname):
        self.csv = ""
        self.dirname = dirname
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        
    def getDay(self, airport, year, month, day):
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
            sys.stderr.write("Error opening %s, skipping.", url)
            return False
        
        self.csv = response.read()
        return True

    def writeDay(self, airport, year, month, day):
        """ write a single day of airport weather to a file """
        fname = "_".join([airport, str(year), str(month), str(day)] + ".csv")
        f = open(self.dirname + "/" + fname, "w")
        f.write(self.csv)

    def dump(self):
        self.csv = ""

    def _isValidDay(self, year, month, day):
        """ returns True if this is a valid day, False otherwise """
        valid = True
        try:
            datetime.date(int(year), int(month), int(day))
        except ValueError:
            valid = False

        return valid

    def getMonth(self, airport, year, month):
        """ gets and writes a month of daily airport weather data """
        for day in xrange(1, 32):
            if self.getDay(airport, year, month, day):
                self.writeDay(airport, year, month, day)
                self.dump()

    def getYear(self, airport, year):
        """ gets and writes a year of daily airport weather data """
        for month in xrange(1, 13):
            self.getMonth(airport, year, month)
