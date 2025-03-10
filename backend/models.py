from sqlalchemy import Column, Integer, String, DateTime
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from database import engine

Base = declarative_base()

class Users(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String)
    password = Column(String)

class Tasks(Base):
    __tablename__ = "Tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(String)
    dateOfCreation = Column(DateTime)
    user_id = Column(Integer)

Base.metadata.create_all(bind=engine)