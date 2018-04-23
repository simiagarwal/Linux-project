import os
import sys

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import datetime
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(250), nullable=False)
    email = Column(String(250), index=True)
    picture = Column(String(250))
    password_hash = Column(String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            '''Valid Token, but expired'''
            return None
        except BadSignature:
            '''Invalid Token'''
            return None
        user_id = data['id']
        return user_id


class Category(Base):

    __tablename__ = 'category'
    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {

            'name': self.name,

            'id': self.id
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250), nullable=False)
    price = Column(String, nullable=False)
    category_name = Column(String(250))
    date_added = Column(DateTime, default=datetime.datetime.now)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return{

            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price

        }


engine = create_engine('sqlite:///catalogwithusers.db')


Base.metadata.create_all(engine)
