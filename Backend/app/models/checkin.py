from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from sqlalchemy import String

class Checkin(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    photo_url = Column(String, nullable=True) 
