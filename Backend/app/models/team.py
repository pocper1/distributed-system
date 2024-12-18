from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from models.association import user_teams  # 引入 user_teams 表
from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from datetime import datetime

class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # 與 Score 之間的一對一關聯
    scores = relationship("Score", back_populates="team")

    # 定義與 Event 的關聯
    event = relationship("Event", back_populates="teams")

    members = relationship("User", secondary=user_teams, back_populates="teams")