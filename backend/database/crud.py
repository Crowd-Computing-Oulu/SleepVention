import uuid
from datetime import datetime
from typing import List, Any

from sqlalchemy import desc
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
        new_activity_row = tables.FitbitActivityLogs(**activity, user_id=user_id)
        db.add(new_activity_row)
        db.commit()
        db.refresh(new_activity_row)


def get_fitbit_heartrate_by_date(db: Session, date_unformatted: str):
    date_formatted = datetime.strptime(date_unformatted, '%Y-%m-%d').date()
    return db.query(tables.FitbitHeartRateLogs).filter(tables.FitbitHeartRateLogs.date == date_formatted).first()


def add_fitbit_heartrate_logs(db: Session, user_id: int, heartrate_logs: List[Any]):
    for hr_log in heartrate_logs:
        if 'restingHeartRate' not in hr_log['value']:
            continue

        # Check if the log with the same date already exists
        hr_db_log = get_fitbit_heartrate_by_date(db, hr_log['dateTime'])
        if hr_db_log:
            hr_db_log.restingHeartRate = hr_log['value']['restingHeartRate']
        else:
            hr_db_log = tables.FitbitHeartRateLogs(**hr_log['value'], dateTime=hr_log['dateTime'], user_id=user_id)

        # Saving the changes to the database
        db.add(hr_db_log)
        db.commit()
        db.refresh(hr_db_log)


def add_fitbit_hrv_logs(db: Session, user_id: int, hrv_logs: List[Any]):
    for hrv_log in hrv_logs:
        # Check if the log with the same date already exists
        hr_db_log = get_fitbit_heartrate_by_date(db, hrv_log['dateTime'])
        if hr_db_log:
            hr_db_log.dailyRmssd = hrv_log['value']['dailyRmssd']
            hr_db_log.deepRmssd = hrv_log['value']['deepRmssd']
        else:
            hr_db_log = tables.FitbitHeartRateLogs(**hrv_log['value'], dateTime=hrv_log['dateTime'], user_id=user_id)

        # Saving the changes to the database
        db.add(hr_db_log)
        db.commit()
        db.refresh(hr_db_log)


def add_fitbit_sleep_levels(db: Session, user_id: int, sleep_id: int, sleep_levels: List[Any]):
    for sleep_level in sleep_levels:
        new_sleep_level = tables.FitbitSleepLevels(**sleep_level, user_id=user_id, sleep_id=sleep_id)
        db.add(new_sleep_level)
        db.commit()
        db.refresh(new_sleep_level)


def add_fitbit_sleep_logs(db: Session, user_id: int, sleep_logs: List[Any]):
    for sleep_log in sleep_logs:
        # Check if the log with the same id already exists
        existing_log = db.query(tables.FitbitSleepLogs).filter(
            tables.FitbitSleepLogs.id == sleep_log['logId']).first()

        # Check if the log has already been added to the database
        if existing_log:
            continue

        if sleep_log['type'] == 'stages' and sleep_log['isMainSleep']:
            # Create new db row if it hasn't added to the database
            new_sleep_log = tables.FitbitSleepLogs(**sleep_log, user_id=user_id)
            db.add(new_sleep_log)
            db.commit()
            db.refresh(new_sleep_log)

            # Extract sleep levels and add them to their corresponding database table
            add_fitbit_sleep_levels(db, user_id, sleep_log['logId'], sleep_log['levels']['data'])


def get_fitbit_activities(db: Session, user_id: int):
    return db.query(tables.FitbitActivityLogs).filter(tables.FitbitActivityLogs.user_id == user_id).order_by(desc(tables.FitbitActivityLogs.date)).all()


def get_fitbit_heartrate_logs(db: Session, user_id: int):
    return db.query(tables.FitbitHeartRateLogs).filter(tables.FitbitHeartRateLogs.user_id == user_id).order_by(desc(tables.FitbitHeartRateLogs.date)).all()


def get_fitbit_sleep_logs(db: Session, user_id: int):
    return db.query(tables.FitbitSleepLogs).filter(tables.FitbitSleepLogs.user_id == user_id).order_by(desc(tables.FitbitSleepLogs.date)).all()


def get_sleep_levels_by_sleep_id(db: Session, sleep_id: int):
    return db.query(tables.FitbitSleepLevels).filter(tables.FitbitSleepLevels.sleep_id == sleep_id).all()


def add_data_file(db: Session, user_id: int, data: schemas.DataFileUploadSchema):
    new_db_row = tables.UserDataFiles(**data.dict(), user_id=user_id)
    db.add(new_db_row)
    db.commit()
    db.refresh(new_db_row)
