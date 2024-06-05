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
