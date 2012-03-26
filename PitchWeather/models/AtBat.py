from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship
from meta import Base

class AtBat(Base):
    __tablename__ = 'atbat'

    inning = Column(Integer)
    num = Column(Integer, primary_key=True)
    b = Column(Integer)
    s = Column(Integer)
    o = Column(Integer)
    batter_id = Column(Integer, ForeignKey('player.id'))
    stand = Column(String(1))
    p_throws = Column(String(1))
    b_height = Column(String(32))
    pitcher_id = Column(Integer, ForeignKey('player.id'))
    des = Column(String(512))
    event = Column(String(128))
    brief_event = Column(String(128))
    game_pk = Column(Integer, ForeignKey('game.game_pk'), primary_key=True)
    game = relationship("Game",
                        primaryjoin="AtBat.game_pk == Game.game_pk")
    batter = relationship("Player",
                          primaryjoin="Player.id == AtBat.batter_id")
    pitcher = relationship("Player",
                           primaryjoin="Player.id == AtBat.pitcher_id")

    __table_args__ = (Index('atbat_game', 'game_pk'),
                      Index('atbat_pitcher', 'pitcher_id'),
                      Index('atbat_batter', 'batter_id'))
    
    def __repr__(self):
        return("<AtBat('%d', '%d', '%d', '%d', '%s')>" %(self.inning,
                                                         self.num,
                                                         self.batter_id,
                                                         self.pitcher_id,
                                                         self.brief_event))

    def load_from_atbat_dict(self, atbat_dict):
        self.inning = atbat_dict['inning']
        self.num = atbat_dict['num']
        self.b = atbat_dict['b']
        self.s = atbat_dict['s']
        self.batter_id = atbat_dict['batter']
        self.stand = atbat_dict['stand']
        self.p_throws = atbat_dict['p_throws']
        self.b_height = atbat_dict['b_height']
        self.pitcher_id = atbat_dict['pitcher']
        self.des = atbat_dict['des']
        self.event = atbat_dict['event']
        self.brief_event = ""
        self.game_pk = atbat_dict['game_pk']
