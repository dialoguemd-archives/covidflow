import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

TRACKER_STORE_USER = os.getenv("SQL_TRACKER_STORE_USER")
TRACKER_STORE_PASSWORD = os.getenv("SQL_TRACKER_STORE_PASSWORD")
TRACKER_STORE_URL = os.getenv("SQL_TRACKER_STORE_URL")
TRACKER_STORE_PORT = os.getenv("SQL_TRACKER_STORE_PORT", "5432")
TRACKER_STORE_DB = os.getenv("SQL_TRACKER_STORE_DB")

CONNECTION_POOL_SIZE = int(os.getenv("SQLALCHEMY_CONNECTION_POOL_SIZE", 15))
CONNECTION_MAX_OVERFLOW = int(os.getenv("SQLALCHEMY_CONNECTION_MAX_OVERFLOW", 15))


engine = create_engine(
    f"postgresql://{TRACKER_STORE_USER}:{TRACKER_STORE_PASSWORD}@{TRACKER_STORE_URL}:{TRACKER_STORE_PORT}/{TRACKER_STORE_DB}",
    pool_size=CONNECTION_POOL_SIZE,
    max_overflow=CONNECTION_MAX_OVERFLOW,
)
_SessionFactory = sessionmaker(bind=engine)


Base = declarative_base()


def session_factory():
    return _SessionFactory()
