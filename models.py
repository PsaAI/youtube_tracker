# models.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Integer

Base = declarative_base()

class Video(Base):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True)
    video_id = Column(String, unique=True)
    title = Column(String)
    link = Column(String)
    published_at = Column(DateTime)
    channel_id = Column(String)

