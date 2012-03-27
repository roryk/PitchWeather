from sqlalchemy import Column, Integer, String, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from meta import Base
from dateutil import parser

# list out what we are expecting because they seem to be missing on a bunch of pitches
PITCH_FIELDS = ['des', 'type', 'tfs_zulu', 'id', 'x', 'y', 'sv_id',
                'start_speed', 'end_speed', 'sz_top', 'sz_bot',
                'pfx_x', 'pfx_z', 'px', 'pz', 'x0', 'y0', 'z0', 'vx0',
                'vy0', 'ax', 'ay', 'az', 'break_y', 'break_angle', 'break_length',
                'pitch_type', 'type_confidence', 'spin_dir', 'spin_rate',
                'nasty', 'on_1b', 'on_2b', 'on_3b']

class Pitch(Base):
    __tablename__ = 'pitch'

    # stuff below here is from the pitch tag in the gameday data
    des = Column(String(256))
    type = Column(String(1))
    tfs_zulu = Column(String(64))
    tfs = Column(Integer(32)) 
    id = Column(Integer, primary_key=True)
    x = Column(Float)
    y = Column(Float)
    sv_id = Column(String(128))
    start_speed = Column(Float)
    end_speed = Column(Float)
    sz_top = Column(Float)
    sz_bot = Column(Float)
    pfx_x = Column(Float)
    pfx_z = Column(Float)
    px = Column(Float)
    pz = Column(Float)
    x0 = Column(Float)
    y0 = Column(Float)
    z0 = Column(Float)
    vx0 = Column(Float)
    vy0 = Column(Float)
    vz0 = Column(Float)
    ax = Column(Float)
    ay = Column(Float)
    az = Column(Float)
    break_y = Column(Float)
    break_angle = Column(Float)
    break_length = Column(Float)
    pitch_type = Column(String(4))
    type_confidence = Column(Float)
    spin_dir = Column(Float)
    spin_rate = Column(Float)
    nasty = Column(Integer)
    on_1b = Column(Integer, ForeignKey('player.id'))
    on_2b = Column(Integer, ForeignKey('player.id'))
    on_3b = Column(Integer, ForeignKey('player.id'))

    # stuff below here i think is derived
    balls = Column(Integer)
    strikes = Column(Integer)
    game_pk = Column(Integer, ForeignKey('game.game_pk'), primary_key=True)
    pitcher_id = Column(Integer, ForeignKey('player.id'))
    batter_id = Column(Integer, ForeignKey('player.id'))
    atbatnum = Column(Integer, ForeignKey('atbat.num'))
    weather_id = Column(Integer, ForeignKey('weather.id'))

    game = relationship("Game",
                        primaryjoin="Game.game_pk == Pitch.game_pk")
    pitcher = relationship("Player",
                           primaryjoin="Player.id == Pitch.pitcher_id")
    batter = relationship("Player",
                          primaryjoin="Player.id == Pitch.batter_id")
    weather = relationship("Weather",
                           primaryjoin="Weather.id == Pitch.weather_id")

    __table_args__ = (Index('pitch_pitcher', 'pitcher_id'),
                      Index('pitch_batter', 'batter_id'),
                      Index('pitch_atbat', 'game_pk', 'atbatnum'))

    def __repr__(self):
        # make this a better representation later
        return("<Pitch(%d, %d, %f)>" %(self.id, self.game_pk, self.end_speed))

    def is_complete(self, pitch_dict):
        for field in PITCH_FIELDS:
            if field not in pitch_dict:
                return False
        return True

    def _convert_value(self, value, fun):
        try:
            converted = fun(value)
        except ValueError:
            converted = None
        return converted

    def load_from_dict(self, pitch_dict):
        self.id = int(pitch_dict['id'])
        self.des = str(pitch_dict['des'])
        self.type = str(pitch_dict['type'])
        utc_time = parser.parse(pitch_dict['tfs_zulu'])
        utc_time = utc_time.replace(tzinfo=None)
        self.tfs_zulu = str(utc_time)
        self.tfs = self._convert_value(pitch_dict['tfs'], int)
        self.x = float(pitch_dict['x'])
        self.y = float(pitch_dict['y'])
        self.sv_id = str(pitch_dict['sv_id'])
        self.start_speed = float(pitch_dict['start_speed'])
        self.end_speed = float(pitch_dict['end_speed'])
        self.sz_top = float(pitch_dict['sz_top'])
        self.sz_bot = float(pitch_dict['sz_bot'])
        self.pfx_x = float(pitch_dict['pfx_x'])
        self.pfx_z = float(pitch_dict['pfx_z'])
        self.px = float(pitch_dict['px'])
        self.pz = float(pitch_dict['pz'])
        self.x0 = float(pitch_dict['x0'])
        self.y0 = float(pitch_dict['y0'])
        self.z0 = float(pitch_dict['z0'])
        self.vx0 = float(pitch_dict['vx0'])
        self.vy0 = float(pitch_dict['vy0'])
        self.vz0 = float(pitch_dict['vz0'])
        self.ax = float(pitch_dict['ax'])
        self.ay = float(pitch_dict['ay'])
        self.az = float(pitch_dict['az'])
        self.break_y = float(pitch_dict['break_y'])
        self.break_angle = float(pitch_dict['break_angle'])
        self.break_length = float(pitch_dict['break_length'])
        self.pitch_type = str(pitch_dict['pitch_type'])
        self.type_confidence = float(pitch_dict['type_confidence'])
        self.spin_dir = float(pitch_dict['spin_dir'])
        self.spin_rate = float(pitch_dict['spin_rate'])
        self.nasty = int(pitch_dict['nasty'])
        
        if pitch_dict['on_1b']:
            self.on_1b = int(pitch_dict['on_1b'])
        if pitch_dict['on_2b']:
            self.on_2b = int(pitch_dict['on_2b'])
        if pitch_dict['on_3b']:
            self.on_3b = int(pitch_dict['on_3b'])

        self.balls = int(pitch_dict['balls'])
        self.strikes = int(pitch_dict['strikes'])
        self.game_pk = int(pitch_dict['game_pk'])

        self.batter_id = int(pitch_dict['batter'])
        self.pitcher_id = int(pitch_dict['pitcher'])
        self.atbatnum = int(pitch_dict['atbatnum'])
