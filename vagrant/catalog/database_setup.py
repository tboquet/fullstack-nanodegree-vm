import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, index=True, unique=True)
    date_added = Column(DateTime, default=datetime.datetime.utcnow)
    image_loc = Column(String(200), nullable=False)

    @property
    def serialize(self):

        return {
            'name': self.name,
            'image_loc': self.image_loc,
            'id': self.id,
        }


class CatalogItem(Base):
    __tablename__ = 'items'

    name = Column(String(80), nullable=False, index=True, unique=True)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    date_added = Column(DateTime, default=datetime.datetime.utcnow)
    image_loc = Column(String(200))
    category_id = Column(Integer, ForeignKey('categories.id'))
    categories = relationship(Category, foreign_keys=[category_id],
                              cascade="all, delete-orphan")

    # We added this serialize function to be able to send JSON objects in a
    # serializable format
    @property
    def serialize(self):

        return {
            'name': self.name,
            'description': self.description,
            'image_loc': self.image_loc,
            'category_id': self.category_id,
            'id': self.id,
        }


engine = create_engine('sqlite:///categorycatalog.db')

Base.metadata.create_all(engine)
