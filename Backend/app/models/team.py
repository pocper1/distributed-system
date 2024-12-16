from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.association import user_teams


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

    # Relationship: 多對多關係
    members = relationship("User", secondary=user_teams, back_populates="teams")
    score = relationship("Score", back_populates="team", uselist=False)

