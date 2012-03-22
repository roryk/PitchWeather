from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

Base = declarative_base()

def init(sqlite_filename):
    engine = create_engine('sqlite:///%s' %(sqlite_filename), echo=False)
    Base.metadata.create_all(engine)

def start(sqlite_filename):
    if not os.path.exists(sqlite_filename):
        init(sqlite_filename)
    engine = create_engine("sqlite:///%s" %(sqlite_filename), echo=False)
    Session = sessionmaker(bind=engine)
    return Session()
