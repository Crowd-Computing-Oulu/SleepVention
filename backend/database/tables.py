from sqlalchemy import Column, String, Boolean, Float, ForeignKey, Date, Integer, DateTime, func
from sqlalchemy.orm import relationship
from database.init import Base


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
    active = Column(Boolean, default=True)

    # Relationship with passwords table
    password = relationship("Passwords", back_populates="user")
    # Relationship with user_information table
    user_information = relationship("UserInformation", back_populates="user")
    # Relationship with login_tokens table
    login_tokens = relationship("LoginTokens", back_populates="user")


class Passwords(Base):
    __tablename__ = 'passwords'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    password = Column(String(255), nullable=False)

    # Relationship with users table
    user = relationship("Users", back_populates="password")


class UserInformation(Base):
    __tablename__ = 'user_information'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    nationality = Column(String(255))
    birth_date = Column(Date)
    gender = Column(String(50))
    height = Column(Float)
    weight = Column(Float)

    # Relationship with users table
    user = relationship("Users", back_populates="user_information")


class LoginTokens(Base):
    __tablename__ = 'login_tokens'

    user_id = Column(Integer, ForeignKey('users.id'))
    token = Column(String(255), primary_key=True)
    created_at = Column(DateTime, default=func.now())
    user_last_visit = Column(DateTime, default=func.now())
    # device_mac_address = Column(String(255), unique=True, nullable=False)

    # Relationship with users table
    user = relationship("Users", back_populates="login_tokens")
