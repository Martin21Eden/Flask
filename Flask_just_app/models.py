from database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.types import DateTime

class User(Base):
    """
    Example Signups table
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    username = Column(String)
    password = Column(String)

    def __repr__(self):
        return "<User(name='%s', email='%s')>" % (
                             self.name, self.email)


class Song(Base):

    __tablename__ = 'songs'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    lyrics = Column(String)
    author = Column(String)

    def __repr__(self):
        return "<User(title='%s', author='%s')>" % (
                             self.title, self.author)
