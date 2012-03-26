from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from meta import Base
import sys

class Stadium(Base):
    __tablename__ = 'stadium'

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    city = Column(String(128))
    state = Column(String(128))
    airport = Column(String(128))
    dome = Column(Boolean)
    team = Column(String(3), ForeignKey('team.code'))

    def loadFromYaml(self, yamlLine):
        self.id = yamlLine['id']
        self.name = yamlLine['park']
        self.city = yamlLine['city']
        self.state = yamlLine['state']
        self.airport = yamlLine['airport']
        self.dome = yamlLine['dome']
        self.team = yamlLine['team']
        
    def __repr__(self):
        return("<Stadium('%s', '%s', '%s', '%s', '%s', '%s')>" %(self.name,
                                               self.city, self.state,
                                               self.airport, self.dome,
                                               self.team))
