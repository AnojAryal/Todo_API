from sqlalchemy import Column, Integer, String, Boolean
from database import Base
from sqlalchemy.orm import relationship


# for todo
class Todo(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    completed = Column(Boolean)
