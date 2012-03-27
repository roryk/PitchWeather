from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, event
import os

Base = declarative_base()

def init(sqlite_filename):
    engine = create_engine('sqlite:///%s' %(sqlite_filename),
                           connect_args={'check_same_thread':False},
                           echo=False,
                           isolation_level='SERIALIZABLE')
    Base.metadata.create_all(engine)

    @event.listens_for(engine, "begin")
    def do_begin(conn):
        conn.execute("BEGIN")
    
    


def start(sqlite_filename):
    if not os.path.exists(sqlite_filename):
        init(sqlite_filename)
    engine = create_engine("sqlite:///%s" %(sqlite_filename), echo=False)
    Session = scoped_session(sessionmaker(bind=engine))
    return Session
