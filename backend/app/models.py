from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    project_name = Column(String, nullable=True)
    location = Column(String, nullable=True)

    category = Column(String, nullable=False)
    urgency = Column(String, nullable=False)
    trade = Column(String, nullable=False)
    summary = Column(Text, nullable=False)

    next_steps = Column(Text, nullable=False)
    tasks = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())