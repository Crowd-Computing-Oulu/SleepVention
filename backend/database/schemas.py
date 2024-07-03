from datetime import date
from typing import Optional

from pydantic import BaseModel


class RegisterSchema(BaseModel):
    """
        Schema representing register/login credentials.

        :ivar username: username of the user.
        :ivar email: Email address of the user.
        :ivar password: Password of the user.
    """
    username: str
    email: str
    password: str


class LoginSchema(BaseModel):
    """
        Schema representing register/login credentials.

        :ivar username: Username of the user.
        :ivar password: Password of the user.
    """
    username: str
    password: str


class UserSchema(BaseModel):
    """
        Schema representing register/login credentials.

        :ivar username: Username of the user.
        :ivar email: Email address of the user.
    """
    username: str
    email: str


class UserInformationSchema(BaseModel):
    nationality: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None


class FitbitTokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class FitbitActivitySchema(BaseModel):
    logId: int
    activityName: str
    calories: Optional[int] = None
    activeDuration: Optional[int] = None
    duration: int
    elevationGain: Optional[int] = None
    startTime: str
    steps: Optional[int] = None
    averageHeartRate: Optional[int] = None
    pace: Optional[float] = None
    speed: Optional[float] = None
