from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

class Event(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    
    # 一个活动对应多个队伍
    teams = relationship('Team', back_populates='event', cascade="all, delete-orphan")