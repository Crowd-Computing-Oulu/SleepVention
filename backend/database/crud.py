import uuid
from datetime import datetime, date, timedelta
from typing import List, Any
import re
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


def save_fitbit_last_update(db: Session, user_id: int, new_date: str, category: str):
    last_updates = db.query(tables.FitbitLastUpdates).filter(tables.FitbitLastUpdates.user_id == user_id).first()

    new_date_obj = None
    if new_date == 'today':
        new_date_obj = date.today()
    elif category == 'activity':
        datetime_match = re.match(r"(\d{4}-\d{2}-\d{2}T)(\d{2}:\d{2}:\d{2})", new_date)
        date_part, _ = datetime_match.groups()
        new_date_obj = datetime.strptime(date_part, '%Y-%m-%dT').date()
    else:
        new_date_obj = datetime.strptime(new_date, '%Y-%m-%d').date()

    if category == 'activity':
        last_updates.activity = new_date_obj
    elif category == 'heartrate':
        last_updates.heart_rate = new_date_obj
    elif category == 'hrv':
        last_updates.hrv = new_date_obj
    elif category == 'sleep':
        last_updates.sleep = new_date_obj

    # Saving the changes to the database
    db.add(last_updates)
    db.commit()
    db.refresh(last_updates)


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

    # Saving the last update
    if len(activities) == 100:
        save_fitbit_last_update(db, user_id, activities[99]['startTime'], 'activity')
    else:
        save_fitbit_last_update(db, user_id, 'today', 'activity')


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

    # Assuming we are not getting data older than 1 year
    save_fitbit_last_update(db, user_id, 'today', 'heartrate')


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

    # Saving the last update
    if len(sleep_logs) == 100:
        save_fitbit_last_update(db, user_id, sleep_logs[99]['dateOfSleep'], 'sleep')
    else:
        save_fitbit_last_update(db, user_id, 'today', 'sleep')


def get_fitbit_activities(db: Session, user_id: int):
    return db.query(tables.FitbitActivityLogs).filter(tables.FitbitActivityLogs.user_id == user_id).order_by(desc(tables.FitbitActivityLogs.date)).all()


def get_fitbit_heartrate_logs(db: Session, user_id: int):
    return db.query(tables.FitbitHeartRateLogs).filter(tables.FitbitHeartRateLogs.user_id == user_id).order_by(desc(tables.FitbitHeartRateLogs.date)).all()


def get_fitbit_sleep_logs(db: Session, user_id: int):
    return db.query(tables.FitbitSleepLogs).filter(tables.FitbitSleepLogs.user_id == user_id).order_by(desc(tables.FitbitSleepLogs.date)).all()


def get_sleep_levels_by_sleep_id(db: Session, sleep_id: int):
    return db.query(tables.FitbitSleepLevels).filter(tables.FitbitSleepLevels.sleep_id == sleep_id).all()


def get_sleep_levels_by_user_id(db: Session, user_id: int):
    return db.query(tables.FitbitSleepLevels).filter(tables.FitbitSleepLevels.user_id == user_id).all()


def add_data_file(db: Session, user_id: int, data: schemas.DataFileUploadSchema):
    new_db_row = tables.UserDataFiles(**data.dict(), user_id=user_id)
    db.add(new_db_row)
    db.commit()
    db.refresh(new_db_row)


def get_data_files(db: Session, user_id: int):
    return db.query(tables.UserDataFiles).filter(tables.UserDataFiles.user_id == user_id).all()


def get_fitbit_last_updates(db: Session, user_id: int):
    last_updates = db.query(tables.FitbitLastUpdates).filter(tables.FitbitLastUpdates.user_id == user_id).first()

    # Create a new object to save last updates of fitbit in the database if it already doesn't exist
    if not last_updates:
        last_updates = tables.FitbitLastUpdates(user_id=user_id)
        db.add(last_updates)
        db.commit()
        db.refresh(last_updates)

    return last_updates


def get_data_privacy_settings(db: Session, user_id: int):
    data_privacy_settings = db.query(tables.DataPrivacySettings).filter(tables.DataPrivacySettings.user_id == user_id).first()

    # Create a new row in the database for data privacy settings if it already doesn't exist
    if not data_privacy_settings:
        data_privacy_settings = tables.DataPrivacySettings(user_id=user_id)
        db.add(data_privacy_settings)
        db.commit()
        db.refresh(data_privacy_settings)

    return data_privacy_settings


def edit_data_privacy_settings(db: Session, user_id: int, data: schemas.EditingDataPrivacySchema):
    data_privacy_settings = get_data_privacy_settings(db, user_id)
    if data.data_category == 'activity':
        data_privacy_settings.activity = not data_privacy_settings.activity
    elif data.data_category == 'heart_rate':
        data_privacy_settings.heart_rate = not data_privacy_settings.heart_rate
    else:
        data_privacy_settings.sleep = not data_privacy_settings.sleep

    db.add(data_privacy_settings)
    db.commit()
    db.refresh(data_privacy_settings)

    return data_privacy_settings


def add_study(db: Session, user_id: int, data: schemas.StudySchema):
    new_db_row = tables.Studies(**data.dict(), user_id=user_id)
    db.add(new_db_row)
    db.commit()
    db.refresh(new_db_row)


def get_own_studies(db: Session, user_id: int):
    return db.query(tables.Studies).filter(tables.Studies.user_id == user_id).all()


def get_study_by_id(db: Session, study_id: int):
    return db.query(tables.Studies).filter(tables.Studies.id == study_id).first()


def delete_study(db: Session, study_id: int):
    study = get_study_by_id(db, study_id)
    if not study:
        return False
    db.delete(study)
    db.commit()
    return True


def add_study_invitation(db: Session, user_id: int, study_id: int):
    existing_invitation = db.query(tables.StudyInvitations).filter_by(invited_user_id=user_id, study_id=study_id).first()
    if existing_invitation:
        return False
    new_invitation = tables.StudyInvitations(invited_user_id=user_id, study_id=study_id)
    db.add(new_invitation)
    db.commit()
    db.refresh(new_invitation)
    return new_invitation


def check_participant_in_study(db: Session, user_id: int, study_id: int):
    count = db.query(tables.study_participants).filter_by(user_id=user_id, study_id=study_id).count()
    return count > 0


def get_user_by_invitation(db: Session, invitation: schemas.StudyInvitationSchema):
    if invitation.username:
        return db.query(tables.Users).filter(tables.Users.username == invitation.username).first()
    else:
        return db.query(tables.Users).filter(tables.Users.email == invitation.email).first()


def get_user_invitations(db: Session, user_id):
    return db.query(tables.StudyInvitations).filter_by(invited_user_id=user_id).all()


def get_invitation_by_user_and_study(db: Session, user_id, study_id):
    return db.query(tables.StudyInvitations).filter_by(study_id=study_id, invited_user_id=user_id).first()


def delete_invitation(db: Session, user_id: int, study_id: int):
    invitation = get_invitation_by_user_and_study(db, user_id, study_id)
    # If the invitation exists, delete it
    if invitation:
        db.delete(invitation)
        db.commit()
        return True
    else:
        return False


def accept_invitation(db: Session, user_id: int, study_id: int):
    # Check if the participant is already in the study
    existing_participant = db.query(tables.study_participants).filter_by(study_id=study_id, user_id=user_id).first()

    if existing_participant:
        return False

    # Add the participant to the study
    new_participant = tables.study_participants.insert().values(study_id=study_id, user_id=user_id)
    db.execute(new_participant)
    db.commit()

    # Remove the invitation
    delete_invitation(db, user_id, study_id)
    return True


def get_public_studies(db: Session):
    return db.query(tables.Studies).filter_by(type='Public').all()
