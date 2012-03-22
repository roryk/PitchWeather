from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float, DateTime
from meta import Base
from Stadium import Stadium

class Weather(Base):
    __tablename__ = 'weather'

    id = Column(Integer, primary_key=True)
    tempF = Column(Float)
    dewF = Column(Float)
    humidity = Column(Float)
    time = Column(DateTime)
    date = Column(Date)
    hour = Column(Integer)
    stadium = Column(Integer, ForeignKey('stadium.id'))
    conditions = Column(String(128))

    def __init__(self):
        pass

    def loadWeatherContainer(self, weatherContainer):
        """ loads a WeatherContainer object """
        self.tempF = weatherContainer.tempF
        self.dewF = weatherContainer.dewF
        self.humidity = weatherContainer.humidity
        self.time = weatherContainer.time
        self.stadium = weatherContainer.stadium
        self.date = weatherContainer.date
        self.hour = weatherContainer.hour
        self.conditions = weatherContainer.conditions

    def __repr__(self):
        return("<Weather('%s', '%f', '%f', '%f', '%s', '%s')>" %(str(self.stadium),
                                                                 self.tempF,
                                                                 self.dewF,
                                                                 self.humidity,
                                                                 str(self.time),
                                                                 self.conditions))
