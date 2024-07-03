import uuid
from typing import List, Any

from sqlalchemy.orm import Session

from database import tables, schemas


def get_user_by_email(db: Session, email: str):
    """
        Retrieves a user by email.

        :param db: Database session.
        :param email: Email address of the user to retrieve.
        :return: User object if found, otherwise None.
    """
    # noinspection PyTypeChecker
    return db.query(tables.Users).filter(tables.Users.email == email).first()


def get_user_by_username(db: Session, username: str):
    """
        Retrieves a user by email.

        :param db: Database session.
        :param username: username of the user to retrieve.
        :return: User object if found, otherwise None.
    """
    # noinspection PyTypeChecker
    return db.query(tables.Users).filter(tables.Users.username == username).first()


def add_user(db: Session, data: schemas.UserSchema):
    user = tables.Users(**data.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_user_password(db: Session, user_id: int, password: str):
    user_password = tables.Passwords(
        user_id=user_id,
        password=password
    )
    db.add(user_password)
    db.commit()
    db.refresh(user_password)
    return user_password


def add_user_information(db: Session, user_id: int):
    user_information = tables.UserInformation(
        user_id=user_id
    )
    db.add(user_information)
    db.commit()
    db.refresh(user_information)
    return user_information


def add_token(db: Session, user_id: int):
    """
       Adds a token for a user.

       :param db: Database session.
       :param user_id: ID of the user for whom the token is being added.
       :return: Token object.
    """
    # noinspection PyTypeChecker
    token = tables.LoginTokens(
        user_id=user_id,
        token=uuid.UUID(str(uuid.uuid4())).hex,
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def get_user_password(db: Session, user_id: int):
    return db.query(tables.Passwords).filter(tables.Passwords.user_id == user_id).first().password


def get_token(db: Session, token_str: str):
    return db.query(tables.LoginTokens).filter(tables.LoginTokens.token == token_str).first()


def get_user_information_by_user_id(db: Session, user_id: int):
    return db.query(tables.UserInformation).filter(tables.UserInformation.user_id == user_id).first()


def edit_user_information(db: Session, user_id: int, data: schemas.UserInformationSchema):
    user_information = db.query(tables.UserInformation).filter(tables.UserInformation.user_id == user_id).first()
    for key, value in data.dict().items():
        setattr(user_information, key, value)
    db.add(user_information)
    db.commit()
    db.refresh(user_information)
    return user_information


def get_fitbit_token_by_user_id(db: Session, user_id: int):
    return db.query(tables.FitbitTokens).filter(tables.FitbitTokens.user_id == user_id).first()


def add_fitbit_token(db: Session, user_id: int, access_token: str, refresh_token: str):
    fitbit_token = db.query(tables.FitbitTokens).filter(tables.FitbitTokens.user_id == user_id).first()
    if not fitbit_token:
        fitbit_token = tables.FitbitTokens(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token
        )
    else:
        fitbit_token.access_token = access_token
        fitbit_token.refresh_token = refresh_token
    db.add(fitbit_token)
    db.commit()
    db.refresh(fitbit_token)
    return fitbit_token


def add_fitbit_user_id(db: Session, user_id: int, fitbit_user_id_str: str):
    fitbit_user_id = tables.FitbitUserId(
        user_id=user_id,
        fitbit_user_id=fitbit_user_id_str
    )
    db.add(fitbit_user_id)
    db.commit()
    db.refresh(fitbit_user_id)
    return fitbit_user_id


def get_fitbit_user_id(db: Session, user_id: int):
    # return db.query(tables.FitbitUserId).filter(tables.FitbitUserId.user_id == user_id).first()
    return '5VYD4S'


def add_fitbit_activities(db: Session, user_id: int, activities: List[Any]):
    for activity in activities:
        # Check if the activity with the same logId already exists
        existing_activity = db.query(tables.FitbitActivityLogs).filter(tables.FitbitActivityLogs.id == activity['logId']).first()
        if existing_activity:
            continue  # Skip this activity if it already exists

        # Create new activity row if it does not exist
        new_activity_row = tables.FitbitActivityLogs(**activity)
        db.add(new_activity_row)
        db.commit()
        db.refresh(new_activity_row)


def get_fitbit_activities(db: Session, user_id: int):
    return db.query(tables.FitbitActivityLogs).all()
