from sqlalchemy import Column, Integer, ForeignKey, String
from meta import Base

class Runner(Base):
    __tablename__ = 'runner'

    id = Column(Integer, ForeignKey('player.id'))
    runner_pk = Column(Integer, primary_key=True)
    atbatnum = Column(Integer, ForeignKey('atbat.num'))
    game_pk = Column(Integer, ForeignKey('game.game_pk'))
    start = Column(String(4))
    end = Column(String(4))
    score = Column(String(1))
    rbi = Column(String(1))
    earned = Column(String(1))
    event = Column(String(128))
    
    def __repr__(self):
        return("<Runner('%d', '%s', '%s', %s')>" %(self.runner_pk,
                                                   self.start,
                                                   self.end,
                                                   self.event))
    def load_from_dict(self, runner_dict):
        self.id = runner_dict['id']
        self.atbatnum = runner_dict['atbatnum']
        self.game_pk = runner_dict['game_pk']
        self.start = runner_dict['start']
        self.end = runner_dict['end']
        self.event = runner_dict['event']
        if "score" in runner_dict:
            self.score = runner_dict['score']
        if "rbi" in runner_dict:
            self.rbi = runner_dict['rbi']
        if "earned" in runner_dict:
            self.earned = runner_dict['earned']
