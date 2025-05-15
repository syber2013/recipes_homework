from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///recipes.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

Base = declarative_base()

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    views = Column(Integer, default=0)
    cooking_time = Column(Integer, default=0)
    ingredients = Column(Text)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

