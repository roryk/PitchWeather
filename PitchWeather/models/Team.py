from sqlalchemy import Column, Integer, String
from meta import Base

class Team(Base):
    __tablename__ = 'team'
    
    code = Column(String(3), primary_key=True)
    name = Column(String(64))
    name_full = Column(String(128))
    name_brief = Column(String(64))
    # one to one relationship with a home stadium
    #stadium = Column(Integer, ForeignKey('stadium.id'))
    #stadium = relationship('Stadium', uselist=False, backref='team')
    #stadium = relationship("Stadium", backref="team",
    #                       primaryjoin="Team.stadium == Stadium.id")
    #stadium = relationship('Stadium', primaryjoin=stadium == Stadium.id)
    
    def __repr__(self):
        return("<Team('%s', '%s', '%s')>" %(self.code, self.name,
                                               self.name_brief))

    def load_from_team_dict(self, team_dict):
        self.code = str(team_dict['code'])
        self.name = str(team_dict['name'])
        self.name_full = str(team_dict['name_full'])
        self.name_brief = str(team_dict['name_brief'])
