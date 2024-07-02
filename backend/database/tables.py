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
    # Relationship with fitbit_tokens table
    fitbit_token = relationship("FitbitTokens", back_populates="user")
    # Relationship with fitbit_sleep_logs table
    fitbit_sleep_logs = relationship("FitbitSleepLogs", back_populates="user")
    fitbit_sleep_levels = relationship("FitbitSleepLevels", back_populates="user")
    fitbit_heart_rate_logs = relationship("FitbitHeartRateLogs", back_populates="user")
    fitbit_activity_logs = relationship("FitbitActivityLogs", back_populates="user")
    fitbit_user_id = relationship("FitbitUserId", back_populates="user")


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


class FitbitUserId(Base):
    __tablename__ = 'fitbit_user_id'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    fitbit_user_id = Column(String(255), unique=True, nullable=False)

    user = relationship("Users", back_populates="fitbit_user_id")


class FitbitTokens(Base):
    __tablename__ = 'fitbit_tokens'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    access_token = Column(String(511), unique=True)
    refresh_token = Column(String(255), unique=True)

    user = relationship("Users", back_populates="fitbit_token")


class FitbitSleepLogs(Base):
    __tablename__ = 'fitbit_sleep_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    dateOfSleep = Column(Date, nullable=False)
    minutesAfterWakeup = Column(Integer, nullable=False)
    minutesAsleep = Column(Integer, nullable=False)
    minutesAwake = Column(Integer, nullable=False)
    minutesToFallAsleep = Column(Integer, nullable=False)
    timeInBed = Column(Integer, nullable=False)
    startTime = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)
    efficiency = Column(Integer, nullable=False)
    deep_count = Column(Integer, nullable=False)
    light_count = Column(Integer, nullable=False)
    rem_count = Column(Integer, nullable=False)
    wake_count = Column(Integer, nullable=False)
    deep_minutes = Column(Integer, nullable=False)
    light_minutes = Column(Integer, nullable=False)
    rem_minutes = Column(Integer, nullable=False)
    wake_minutes = Column(Integer, nullable=False)

    user = relationship("Users", back_populates="fitbit_sleep_logs")
    sleep_levels = relationship("FitbitSleepLevels", back_populates="parent_sleep_log")


class FitbitSleepLevels(Base):
    __tablename__ = 'fitbit_sleep_levels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sleep_id = Column(Integer, ForeignKey('fitbit_sleep_logs.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    dateTime = Column(DateTime, nullable=False)
    level = Column(String(15), nullable=False)
    seconds = Column(Integer, nullable=False)

    parent_sleep_log = relationship("FitbitSleepLogs", back_populates="sleep_levels")
    user = relationship("Users", back_populates="fitbit_sleep_levels")


class FitbitHeartRateLogs(Base):
    __tablename__ = 'fitbit_heart_rate_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    datetime = Column(Date, nullable=False)
    restingHeartRate = Column(Integer)
    dailyRmssd = Column(Float)
    deepRmssd = Column(Float)

    user = relationship("Users", back_populates="fitbit_heart_rate_logs")


class FitbitActivityLogs(Base):
    __tablename__ = 'fitbit_activity_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    activityName = Column(String(15))
    calories = Column(Integer)
    activeDuration = Column(Integer)
    duration = Column(Integer, nullable=False)
    elevationGain = Column(Integer)
    startTime = Column(DateTime, nullable=False)
    steps = Column(Integer)
    averageHeartRate = Column(Integer)
    pace = Column(Float)
    speed = Column(Float)

    user = relationship("Users", back_populates="fitbit_activity_logs")
