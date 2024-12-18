from sqlalchemy import Table, Column, Integer, ForeignKey
from database import Base

# user_teams 中间表，用于存储 User 和 Team 的多对多关系
user_teams = Table(
    'user_teams', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('team_id', Integer, ForeignKey('teams.id', ondelete='CASCADE'), primary_key=True)
)