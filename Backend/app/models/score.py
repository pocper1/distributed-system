from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey

class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    score = Column(Float, nullable=False)

    # 與 Team 的反向關聯
    team = relationship("Team", back_populates="scores")