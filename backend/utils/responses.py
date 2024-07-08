from datetime import date, time, datetime
from typing import Optional

from pydantic import BaseModel

from database import tables, schemas


class LoginResponseSchema(BaseModel):
    """
        Schema representing the response to a login request.

        :param user_id: Unique identifier for the user.
        :param token: Authentication token.
    """
    user_id: int
    token: str

    class Config:
        from_attributes = True


class UserProfileResponseSchema(BaseModel):
    username: str
    email: str
    nationality: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None

    class Config:
        from_attributes = True

    def set_user_information(self, user_information):
        self.nationality = user_information.nationality
        self.birth_date = user_information.birth_date
        self.gender = user_information.gender
        self.height = user_information.height
        self.weight = user_information.weight


class FitbitActivityResponseSchema(BaseModel):
    activityName: str
    date: date
    calories: Optional[int] = None
    activeDuration: Optional[int] = None
    duration: int
    elevationGain: Optional[float] = None
    startTime: time
    steps: Optional[int] = None
    averageHeartRate: Optional[int] = None
    pace: Optional[float] = None
    speed: Optional[float] = None

    class Config:
        from_attributes = True


class FitbitHeartrateResponseSchema(BaseModel):
    date: date
    restingHeartRate: Optional[int] = None
    dailyRmssd: Optional[float] = None
    deepRmssd: Optional[float] = None

    class Config:
        from_attributes = True


class FitbitSleepResponseSchema(BaseModel):
    date: date  # dateOfSleep
    minutesAfterWakeup: Optional[int] = None
    minutesAsleep: Optional[int] = None
    minutesAwake: Optional[int] = None
    minutesToFallAsleep: Optional[int] = None
    timeInBed: Optional[int] = None
    startTime: datetime
    endTime: Optional[datetime] = None
    duration: int
    efficiency: Optional[int] = None
    deep_count: Optional[int] = None
    light_count: Optional[int] = None
    rem_count: Optional[int] = None
    wake_count: Optional[int] = None
    deep_minutes: Optional[int] = None
    light_minutes: Optional[int] = None
    rem_minutes: Optional[int] = None
    wake_minutes: Optional[int] = None

    class Config:
        from_attributes = True
