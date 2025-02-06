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
    prolific_id: Optional[str] = None
    nationality: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None


class FitbitTokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class DataFileUploadSchema(BaseModel):
    file_name: str
    file_content: str

    class Config:
        from_attributes = True


class EditingDataPrivacySchema(BaseModel):
    data_category: str


class StudySchema(BaseModel):
    name: str
    description: str
    type: str
    consent_form_link: str

    class Config:
        from_attributes = True


class StudyInvitationSchema(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
