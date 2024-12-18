from sqlalchemy import Boolean, Column, Integer, String, DateTime
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
    is_superadmin = Column(Boolean, default=False)

    # 多对多关系，User 与 Team 通过 user_teams 关联
    teams = relationship("Team", secondary=user_teams, back_populates="members")

    def create(self, db, username, email, password, team_id=None):
        """
        创建新用户
        """
        user = User(username=username, email=email, password=password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def login(self, db, email, password):
        """
        验证用户的登录凭据
        """
        user = db.query(User).filter(User.email == email).first()
        if not user or user.password != password:
            return None
        return user

    def edit(self, db, user_id, **kwargs):
        """
        编辑用户信息
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