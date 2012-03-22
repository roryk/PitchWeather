from sqlalchemy import Column, Integer, String, Float, Index, ForeignKey
from meta import Base

class PlayerInGame(Base):
    __tablename__ = 'playeringame'

    id = Column(Integer, ForeignKey('player.id'), primary_key=True)
    num = Column(Integer)
    position = Column(String(2))
    bat_order = Column(Integer)
    game_position = Column(String(2))
    avg = Column(Float)
    hr = Column(Integer)
    rbi = Column(Integer)
    wins = Column(Integer)
    losses = Column(Integer)
    era = Column(Float)
    game_pk = Column(Integer, ForeignKey('game.game_pk'), primary_key=True)

    __table__args__ = (Index('playeringame_player', 'id'),
                       Index('playeringame_game', 'game'))

    # change this so it looks up the players name maybe
    def __repr__(self):
        return("<PlayerInGame('%d', '%s', '%d')>" %(self.id,
                                                    self.position,
                                                    self.game_pk))
