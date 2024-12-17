from sqlalchemy import Column, Integer, String, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from models.association import user_teams

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship: 多對多關係
    teams = relationship("Team", secondary=user_teams, back_populates="members")

    def create(self, db, username, email, password, team_id=None):
        """
        Create a new user.
        """
        user = User(username=username, email=email, password=password, team_id=team_id)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def login(self, db, email, password):
        """
        Validate login credentials.
        """
        user = db.query(User).filter(User.email == email).first()
        if not user or user.password != password:
            return None
        return user

    def edit(self, db, user_id, **kwargs):
        """
        Edit user details.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user
