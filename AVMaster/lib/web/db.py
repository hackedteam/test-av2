from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from settings import SQLALCHEMY_DATABASE_URI

engine = create_engine('%s' % SQLALCHEMY_DATABASE_URI, convert_unicode=True,
						pool_size=20, max_overflow=0,
						poolclass=NullPool)

#engine = create_engine('mysql://avmonitor:avmonitorp123@localhost:3306/avmonitor', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)