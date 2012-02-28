from urllib2 import urlopen
import os

class WeatherGetter(object):

    baseurl = "http://www.wunderground.com/history/airport"

    def __init__(self, dirname):
        self.csv = ""
        self.dirname = dirname
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        
    def get(self, airport, year, month, day):
        url = "/".join([self.baseurl, airport,
                       str(year), str(month), str(day),
                        "DailyHistory.html?format=1"])
        print url
        response = urlopen(url)
        self.csv = response.read()

    def write(self, airport, year, month, day):
        fname = "_".join([airport, str(year), str(month), str(day), ".csv"])
        f = open(self.dirname + "/" + fname, "w")
        f.write(self.csv)

    def dump(self):
        self.csv = ""
