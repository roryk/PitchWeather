from sqlalchemy import Column, Integer, String, ForeignKey, Index
from meta import Base

class AtBat(Base):
    __tablename__ = 'atbat'

    inning = Column(Integer)
    num = Column(Integer, primary_key=True)
    b = Column(Integer)
    s = Column(Integer)
    o = Column(Integer)
    batter = Column(Integer, ForeignKey('player.id'))
    stand = Column(String(1))
    p_throws = Column(String(1))
    b_height = Column(String(32))
    pitcher = Column(Integer, ForeignKey('player.id'))
    des = Column(String(512))
    event = Column(String(128))
    brief_event = Column(String(128))
    game_pk = Column(Integer, ForeignKey('game.game_pk'), primary_key=True)

    __table_args__ = (Index('atbat_game', 'game_pk'),
                      Index('atbat_pitcher', 'pitcher'),
                      Index('atbat_batter', 'batter'))
    
    def __repr__(self):
        return("<AtBat('%d', '%d', '%d', '%d', '%s')>" %(self.inning,
                                                         self.num,
                                                         self.batter,
                                                         self.pitcher,
                                                         self.brief_event))

    def load_from_atbat_dict(self, atbat_dict):
        self.inning = atbat_dict['inning']
        self.num = atbat_dict['num']
        self.b = atbat_dict['b']
        self.s = atbat_dict['s']
        self.batter = atbat_dict['batter']
        self.stand = atbat_dict['stand']
        self.p_throws = atbat_dict['p_throws']
        self.b_height = atbat_dict['b_height']
        self.pitcher = atbat_dict['pitcher']
        self.des = atbat_dict['des']
        self.event = atbat_dict['event']
        self.brief_event = ""
        self.game_pk = atbat_dict['game_pk']
