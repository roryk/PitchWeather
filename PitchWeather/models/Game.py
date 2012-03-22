from sqlalchemy import Column, Integer, String, ForeignKey, Index, Date
from meta import Base
from dateutil import parser

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
    stadium = Column(Integer, ForeignKey('stadium.id'))
    date = Column(Date)
    league = Column(String(32))
    status = Column(String(10))
    start_time_est = Column(Date)

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
        self.stadium = int(gamefile.boxscore['venue_id'])
        self.status = str(gamefile.boxscore['status_ind'])
        date = (str(gamefile.boxscore['date']) + " " +
                str(gamefile.game['game_time_et']) + " EST")
        self.start_time_est = parser.parse(date)
