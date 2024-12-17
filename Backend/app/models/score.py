from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Score(Base):
    __tablename__ = "scores"

    team_id = Column(Integer, ForeignKey("teams.id"), primary_key=True)  # Primary key linked to team_id
    score = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with the Team model
    team = relationship("Team", back_populates="score")
