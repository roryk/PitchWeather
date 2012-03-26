from sqlalchemy import (Column, Integer, String, ForeignKey, Date, Float, DateTime)
from sqlalchemy.orm import relationship
from meta import Base

class Weather(Base):
    __tablename__ = 'weather'

    id = Column(Integer, primary_key=True)
    tempF = Column(Float)
    dewF = Column(Float)
    humidity = Column(Float)
    time = Column(DateTime)
    date = Column(Date)
    hour = Column(Integer)
    stadium_id = Column(Integer, ForeignKey('stadium.id'))
    conditions = Column(String(128))
    stadium = relationship("Stadium",
                           primaryjoin="Stadium.id == Weather.stadium_id")

    def __init__(self):
        pass
    
    def loadWeatherContainer(self, weatherContainer):
        """ loads a WeatherContainer object """
        self.tempF = weatherContainer.tempF
        self.dewF = weatherContainer.dewF
        self.humidity = weatherContainer.humidity
        self.time = weatherContainer.time
        self.stadium_id = weatherContainer.stadium
        self.date = weatherContainer.date
        self.hour = weatherContainer.hour
        self.conditions = weatherContainer.conditions

    def __repr__(self):
        return("<Weather('%s', '%s', '%s', '%s', '%s', '%s')>" %(str(self.stadium),
                                                                 str(self.tempF),
                                                                 str(self.dewF),
                                                                 str(self.humidity),
                                                                 str(self.time),
                                                                 self.conditions))
