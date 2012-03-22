from sqlalchemy import Column, Integer, String
from meta import Base

class Player(Base):
    __tablename__ = 'player'
    
    id = Column(Integer, primary_key=True)
    first = Column(String(64))
    last = Column(String(64))
    boxname = Column(String(64))
    rl = Column(String(1))

    def __repr__(self):
        return("<Player('%s', '%s', '%s')>" %(self.first, self.last,
                                              self.boxname))

    def load_from_player_dict(self, player_dict):
        self.id = str(player_dict['id'])
        self.first = str(player_dict['first'])
        self.last = str(player_dict['last'])
        self.boxname = str(player_dict['boxname'])
        self.rl = str(player_dict['rl'])
