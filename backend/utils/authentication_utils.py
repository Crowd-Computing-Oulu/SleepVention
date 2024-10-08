import typing
import datetime

from fastapi import Request, HTTPException

from database import crud


def get_token(request: Request):
    token: typing.Optional[str] = request.headers.get('token')
    if not token:
        raise HTTPException(status_code=401, detail='Unauthorized')
    return token


def verify_token(token_str: str, db):
    token = crud.get_token(db, token_str)
    if not token:
        raise HTTPException(status_code=401, detail='Invalid token')
    if token.created_at + datetime.timedelta(days=1) < datetime.datetime.utcnow():
        raise HTTPException(status_code=401, detail='Invalid token')
    return token


def get_current_user_by_token(token_str: str, db):
    token = verify_token(token_str, db)
    return token.user


def get_current_user(request: Request, db):
    token_str = get_token(request)
    return get_current_user_by_token(token_str, db)


def check_study_creator(user_id: int, study_id: int, db):
    study = crud.get_study_by_id(db, study_id)
    if not study:
        raise HTTPException(status_code=404, detail='Study not found')

    return study.user_id == user_id
