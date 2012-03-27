from sqlalchemy import Column, Integer, String, ForeignKey, Index, Date
from sqlalchemy.orm import relationship
from meta import Base
from dateutil import parser

GAME_FIELDS = ['game_pk', 'type', 'away_team_code', 'home_team_code',
               'away_fname', 'home_fname', 'away_sname', 'home_sname',
               'stadium_id', 'date', 'league', 'status', 'start_time_est']

class Game(Base):
    __tablename__ = 'game'
    
    game_pk = Column(Integer, primary_key=True)
    type = Column(String(1))
    away_team_code = Column(String(3), ForeignKey('team.code'))
    home_team_code = Column(String(3), ForeignKey('team.code'))
    away_fname = Column(String(42))
    home_fname = Column(String(42))
    away_sname = Column(String(16))
    home_sname = Column(String(16))
    stadium_id = Column(Integer, ForeignKey('stadium.id'))
    date = Column(Date)
    league = Column(String(32))
    status = Column(String(10))
    start_time_est = Column(Date)

    stadium = relationship("Stadium",
                           primaryjoin="Stadium.id == Game.stadium_id")

    __table_args__ = (Index('game_away', 'away_team_code'),
                      Index('game_home', 'home_team_code'))

    def __repr__(self):
        return("<Game('%d', '%s', '%s', '%s'>" %(self.game_pk,
                                                 self.home_team_code,
                                                 self.away_team_code,
                                                 self.date))

    def load_from_gameday_object(self, gamefile):
        self.game_pk = int(gamefile.game['game_pk'])
        self.type = str(gamefile.game['type'])
        self.away_team_code = str(gamefile.boxscore['away_team_code'])
        self.home_team_code = str(gamefile.boxscore['home_team_code'])
        self.away_fname = str(gamefile.boxscore['away_fname'])
        self.home_fname = str(gamefile.boxscore['home_fname'])
        self.home_sname = str(gamefile.boxscore['home_sname'])
        self.away_sname = str(gamefile.boxscore['away_sname'])
        self.league = str(gamefile.boxscore['home_sport_code'])
        self.date = parser.parse(gamefile.boxscore['date'])
        self.stadium_id = int(gamefile.boxscore['venue_id'])
        self.status = str(gamefile.boxscore['status_ind'])
        date = (str(gamefile.boxscore['date']) + " " +
                str(gamefile.game['game_time_et']) + " EST")
        self.start_time_est = parser.parse(date)

    def is_complete(self, gameday_object):
        for field in GAME_FIELDS:
            if(field not in gameday_object.boxscore or
               field not in gameday_object.game):
                return False
        return True
