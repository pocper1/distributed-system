from sqlalchemy import Table, Column, Integer, ForeignKey, Float
from database import Base

user_teams = Table(
    "user_teams",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("team_id", Integer, ForeignKey("teams.id"), nullable=False)
)
