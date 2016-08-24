import sys
import sqlalchemy
import sqlalchemy.ext.declarative

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Brewery(Base):
    __tablename__ = 'breweries'

    name = Column(
        String(80), nullable=False)
    id = Column(
        Integer, primary_key=True)


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


#### INSERT at end of file ####
engine = create_engine(
    'sqlite:///brew.db'
)

Base.metadata.create_all(engine)
