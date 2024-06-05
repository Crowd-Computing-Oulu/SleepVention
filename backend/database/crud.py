import uuid

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
