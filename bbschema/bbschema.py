from sqlalchemy import Base, Column, Integer, String

class Stadium(Base):
    """ database ORM describing a MLB stadium """
    __tablename__ = 'stadium'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    location = Column(String)
    airport = Column(String)

    def __init__(self):
        pass

    def __repr__(self):
        return("<Stadium('%s', '%s', '%s', '%s')>" %(self.name, self.location,
                                                     self.airport))
