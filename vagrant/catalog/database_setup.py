import sys
import sqlalchemy
import sqlalchemy.ext.declarative

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Brewery(Base):
    __tablename__ = 'breweries'

    name = Column(
        String(80), nullable=False)
    id = Column(
        Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
        }


class Beer(Base):
    __tablename__ = 'beers'

    name = Column(
        String(80), nullable=False)
    id = Column(
        Integer, primary_key=True)
    style = Column(
        String(80))
    brewery_id = Column(
        Integer, ForeignKey('breweries.id'))
    brewery = relationship(Brewery)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'style': self.style
        }


#### INSERT at end of file ####
engine = create_engine(
    'sqlite:///brew.db',
    convert_unicode=True
)

Base.metadata.create_all(engine)
