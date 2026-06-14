from sqlalchemy import Column, Integer, String
from database.db import Base

from sqlalchemy import Column, Integer, String, Boolean
from database.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    is_admin = Column(Boolean, default=False)


class Equipment(Base):
    __tablename__ = "equipments"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    status = Column(String)
    location = Column(String)
    last_maintenance = Column(String)

class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True)
    equipment_name = Column(String)
    description = Column(String)
    status = Column(String)