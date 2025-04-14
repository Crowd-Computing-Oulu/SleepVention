from datetime import datetime, date, timedelta
import re
from sqlalchemy import Column, String, Boolean, Float, ForeignKey, Date, Integer, DateTime, func, Time, Text, Table
from sqlalchemy.orm import relationship
from database.init import Base


study_participants = Table(
    'study_participants', Base.metadata,
    Column('study_id', Integer, ForeignKey('studies.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('participant_identifier', String(255))
)


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
    uploaded_data_files = relationship("UserDataFiles", back_populates="user")
    fitbit_last_updates = relationship("FitbitLastUpdates", back_populates="user")
    data_privacy_settings = relationship("DataPrivacySettings", back_populates="user")
    own_studies = relationship("Studies", back_populates="creator")
    participated_studies = relationship("Studies", secondary=study_participants, back_populates="participants")
    invitations = relationship("StudyInvitations", back_populates="invited_user")


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
    prolific_id = Column(String(255))

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
    code_verifier = Column(String(255))
    access_token = Column(String(511), unique=True)
    refresh_token = Column(String(255), unique=True)

    user = relationship("Users", back_populates="fitbit_token")


class FitbitSleepLogs(Base):
    __tablename__ = 'fitbit_sleep_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    date = Column(Date, nullable=False)  # dateOfSleep
    minutesAfterWakeup = Column(Integer)
    minutesAsleep = Column(Integer)
    minutesAwake = Column(Integer)
    minutesToFallAsleep = Column(Integer)
    timeInBed = Column(Integer)
    startTime = Column(DateTime, nullable=False)
    endTime = Column(DateTime)
    duration = Column(Integer, nullable=False)
    efficiency = Column(Integer)
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

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'logId':
                self.id = value

            elif key == 'dateOfSleep':
                self.date = datetime.strptime(value, '%Y-%m-%d').date()

            elif key == 'startTime' or key == 'endTime':
                date_obj = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
                setattr(self, key, date_obj)

            elif key == 'levels':
                self.deep_count = value['summary']['deep']['count']
                self.light_count = value['summary']['light']['count']
                self.rem_count = value['summary']['rem']['count']
                self.wake_count = value['summary']['wake']['count']

                self.deep_minutes = value['summary']['deep']['minutes']
                self.light_minutes = value['summary']['light']['minutes']
                self.rem_minutes = value['summary']['rem']['minutes']
                self.wake_minutes = value['summary']['wake']['minutes']

            else:
                setattr(self, key, value)


class FitbitSleepLevels(Base):
    __tablename__ = 'fitbit_sleep_levels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sleep_id = Column(Integer, ForeignKey('fitbit_sleep_logs.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    dateTime = Column(DateTime, nullable=False)
    level = Column(String(255), nullable=False)
    seconds = Column(Integer, nullable=False)

    parent_sleep_log = relationship("FitbitSleepLogs", back_populates="sleep_levels")
    user = relationship("Users", back_populates="fitbit_sleep_levels")

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'dateTime':
                date_obj = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
                setattr(self, key, date_obj)
            else:
                setattr(self, key, value)


class FitbitHeartRateLogs(Base):
    __tablename__ = 'fitbit_heart_rate_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    date = Column(Date, unique=True)
    restingHeartRate = Column(Integer)
    dailyRmssd = Column(Float)
    deepRmssd = Column(Float)

    user = relationship("Users", back_populates="fitbit_heart_rate_logs")

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'dateTime':
                self.date = datetime.strptime(value, '%Y-%m-%d').date()
            else:
                setattr(self, key, value)


class FitbitActivityLogs(Base):
    __tablename__ = 'fitbit_activity_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    date = Column(Date, nullable=False)
    activityName = Column(String(255), nullable=False)
    calories = Column(Integer)
    activeDuration = Column(Integer)
    duration = Column(Integer, nullable=False)
    elevationGain = Column(Float)
    startTime = Column(Time, nullable=False)
    steps = Column(Integer)
    averageHeartRate = Column(Integer)
    pace = Column(Float)
    speed = Column(Float)

    user = relationship("Users", back_populates="fitbit_activity_logs")

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'logId':
                self.id = value
            elif key == 'startTime':
                # extracting the date and time from the response
                datetime_match = re.match(r"(\d{4}-\d{2}-\d{2}T)(\d{2}:\d{2}:\d{2})", value)
                date_part, time_part = datetime_match.groups()
                date_obj = datetime.strptime(date_part, '%Y-%m-%dT').date()
                time_obj = datetime.strptime(time_part, '%H:%M:%S').time()
                self.date = date_obj
                self.startTime = time_obj
            else:
                setattr(self, key, value)


class FitbitLastUpdates(Base):
    __tablename__ = 'fitbit_last_updates'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    activity = Column(Date)
    heart_rate = Column(Date)
    hrv = Column(Date)
    sleep = Column(Date)

    user = relationship("Users", back_populates="fitbit_last_updates")

    def __init__(self, user_id):
        self.user_id = user_id
        self.activity = date.today() - timedelta(days=60)
        self.heart_rate = date.today() - timedelta(days=60)
        self.hrv = date.today() - timedelta(days=60)
        self.sleep = date.today() - timedelta(days=60)
            

class UserDataFiles(Base):
    __tablename__ = 'user_data_files'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    file_name = Column(String(255), nullable=False)
    file_content = Column(Text, nullable=False)

    user = relationship("Users", back_populates="uploaded_data_files")


class DataPrivacySettings(Base):
    __tablename__ = 'data_privacy_settings'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

    # True means public and false is private
    activity = Column(Boolean, default=False)
    heart_rate = Column(Boolean, default=False)
    sleep = Column(Boolean, default=False)

    user = relationship("Users", back_populates="data_privacy_settings")


class Studies(Base):
    __tablename__ = 'studies'

    user_id = Column(Integer, ForeignKey('users.id'))

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_date = Column(Date, default=func.current_date(), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    type = Column(String(255), nullable=False)  # Can be 'Public' or 'Private'
    consent_form_link = Column(String(255), nullable=False)
    participant_id_required = Column(Boolean, default=False)

    creator = relationship("Users", back_populates="own_studies")
    participants = relationship("Users", secondary=study_participants, back_populates="participated_studies")
    invitations = relationship("StudyInvitations", back_populates="study")


class StudyInvitations(Base):
    __tablename__ = 'study_invitations'

    invited_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    study_id = Column(Integer, ForeignKey('studies.id'), nullable=False)

    id = Column(Integer, primary_key=True, autoincrement=True)
    invitation_time = Column(DateTime, default=func.now(), nullable=False)

    invited_user = relationship("Users", back_populates="invitations")
    study = relationship("Studies", back_populates="invitations")
