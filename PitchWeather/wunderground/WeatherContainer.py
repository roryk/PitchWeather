from dateutil import parser

class WeatherContainer(object):

    def __init__(self, line):
        from WeatherGetter import WEATHERHEADER
        
        for key in WEATHERHEADER:
            setattr(self, key, line[key])

        self.tempF = self._str2float(self.tempF)
        self.dewF = self._str2float(self.dewF)
        self.humidity = self._str2float(self.humidity)
        self.pressure = self._str2float(self.pressure)
        self.visibility = self._str2float(self.visibility)
        self.windSpeed = self._str2float(self.windSpeed)
        self.gustSpeed = self._str2float(self.gustSpeed)
        self.precip = self._str2float(self.precip)
        self.windDirDeg = self._str2float(self.windDirDeg)
        #self.timeUTC = datetime.datetime.strptime(self.timeUTC, '%Y-%m-%d %H:%M:%S')
        self.timeUTC = parser.parse(self.timeUTC + "Z" + "+00:00")
        self.airport = None
        self.stadium = None

    def _str2float(self, field):
        try:
            field = float(field)
        except ValueError:
            field = 0.0
        return field
    
    def __repr__(self):
        return("<Weather('%s', '%f', '%f', '%s')>" %(self.timeUTC,
                                                     self.tempF,
                                                     self.humidity,
                                                     self.conditions))

    def __getTime(self):
        return self.timeUTC
    time = property(__getTime)

    def __getHour(self):
        return self.timeUTC.hour
    hour = property(__getHour)

    def __getDate(self):
        return self.timeUTC.date()
    date = property(__getDate)
