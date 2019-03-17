#!/usr/bin/python
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
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

    UniqueConstraint(email, name)


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    UniqueConstraint(name)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name
        }


class CatItem(Base):
    __tablename__ = 'category_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    cat_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category", cascade="all, delete")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    UniqueConstraint(cat_id, name)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'cat_id': self.cat_id,
            'description': self.description,
            'id': self.id,
            'title': self.name
        }


engine = create_engine('sqlite:///categorycatalogwithusers.db')


Base.metadata.create_all(engine)
