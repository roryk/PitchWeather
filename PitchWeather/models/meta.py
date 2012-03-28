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

def page_query(q):
    """
    return a subset of items from queries that will return too many rows
    code lifted from:
    http://stackoverflow.com/questions/1145905/scanning-huge-tables-with-\
    sqlalchemy-using-the-orm
    """
    offset = 0
    while True:
        for elem in q.limit(1000).offset(offset):
           r = True
           yield elem
        offset += 1000
        if not r:
            break
        r = False
