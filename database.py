import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///publish_jobs.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """
    Creates all SQLAlchemy-mapped tables that do not already exist.
    Model modules MUST be imported before this call so their classes
    are registered against Base.metadata.
    """
    # Import all ORM models so SQLAlchemy registers their tables
    from models.publish_job import PublishJob  # noqa: F401
    Base.metadata.create_all(bind=engine)
