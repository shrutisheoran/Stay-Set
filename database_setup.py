'''
    Four tables:
        -> category
        -> subCategory
        -> items
        -> users
    are created in the following code
'''
# Importing Necessary Libraries

import sys

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime

from sqlalchemy.sql import func

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import create_engine

from sqlalchemy.orm import relationship

# Initialising Base with declarative_base() method
Base = declarative_base()

# Handling table Users


class Users(Base):
    __tablename__ = 'users'

    name = Column(String(20))
    id = Column(Integer, primary_key=True)
    picture = Column(String(200))
    email = Column(String(80), nullable=False)

# Handling table Category


class Category(Base):
    __tablename__ = 'category'

    name = Column(String(50), nullable=False)
    id = Column(Integer, primary_key=True)
    picture = Column(String(200))
    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship(Users)
    # Returning Columns in Json format

    @property
    def serialize(self):
        return {
            'name': self.name,
            'picture': self.picture,
            'id': self.id,
        }

# Handling table SubCategory


class SubCategory(Base):
    __tablename__ = 'sub_category'

    name = Column(String(50), nullable=False)
    id = Column(Integer, primary_key=True)
    picture = Column(String(200))
    user_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('category.id'))
    users = relationship(Users)
    category = relationship(Category)

    @property
    # Returning Columns in Json format
    def serialize(self):
        return {
            'name': self.name,
            'picture': self.picture,
            'id': self.id,
        }

# Handling table Items


class Items(Base):
    __tablename__ = 'items'

    name = Column(String(100), nullable=False)
    id = Column(Integer, primary_key=True)
    picture = Column(String(200))
    description = Column(String(150))
    price = Column(String(20), nullable=False)
    rating = Column(Integer)
    seller_name = Column(String(20), nullable=False)
    seller_phoneno = Column(String(20), nullable=False)
    creation_time = Column(DateTime(timezone=True), server_default=func.now())
    updation_time = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))
    subCategory_id = Column(Integer, ForeignKey('sub_category.id'))
    category_id = Column(Integer, ForeignKey('category.id'))
    users = relationship(Users)
    sub_category = relationship(SubCategory)
    category = relationship(Category)
    # Returning Columns in Json format

    @property
    def serialize(self):
        return {
            'name': self.name,
            'picture': self.picture,
            'price': self.price,
            'id': self.id,
            'description': self.description,
            'Seller': self.seller_name,
            'Seller Phone No': self.seller_phoneno,
        }


'''
    Create Engine and then bind it to the base class so that the declaratives
    can be accessed through a dbsession instance
'''

engine = create_engine(
                        'postgresql://postgres:happynewid@localhost/shoppingsite')  # noqa

Base.metadata.create_all(engine)
