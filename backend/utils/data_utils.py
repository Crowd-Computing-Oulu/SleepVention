from typing import List

import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from database import crud, schemas
from datetime import date, timedelta

FITBIT_CLIENT_ID = '23PDRW'
FITBIT_CLIENT_SECRET = '5cff99a1510ed622f0abee34f0e68997'
PKCE_CODE_VERIFIER = '0n5r552d051q3e4l6a3t0x45224b5d4r3g4d2b0u3a2m012g6g4m6q3n4c5s0x1z5u42316v65465y260y4j0u0s0y6o261w0y5t1p66374a194f6m3m522u6x090k0x'
FITBIT_GET_TOKEN_URL = 'https://api.fitbit.com/oauth2/token'
Fitbit_BASE_URL = 'https://api.fitbit.com'


def get_fitbit_token(fitbit_code) -> schemas.FitbitTokenSchema:
    headers = {
        'Authorization': 'Basic MjNQRFJXOjVjZmY5OWExNTEwZWQ2MjJmMGFiZWUzNGYwZTY4OTk3',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'client_id': FITBIT_CLIENT_ID,
        'grant_type': 'authorization_code',
        'code': fitbit_code,
        'code_verifier': PKCE_CODE_VERIFIER
    }
    response = requests.post(FITBIT_GET_TOKEN_URL, headers=headers, data=data)
    if response.status_code == 200:
        fitbit_token = schemas.FitbitTokenSchema(**response.json())
        return fitbit_token
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


def refresh_fitbit_token(fitbit_token) -> schemas.FitbitTokenSchema:
    refresh_token_str = fitbit_token.refresh_token
    headers = {
        'Authorization': 'Basic MjNQRFJXOjVjZmY5OWExNTEwZWQ2MjJmMGFiZWUzNGYwZTY4OTk3',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'client_id': FITBIT_CLIENT_ID,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token_str
    }
    response = requests.post(FITBIT_GET_TOKEN_URL, headers=headers, data=data)
    if response.status_code == 200:
        fitbit_token = schemas.FitbitTokenSchema(**response.json())
        return fitbit_token
    else:
        raise HTTPException(status_code=403, detail="Server failed to get access to the Fitbit API")


def get_fitbit_activities(headers, start_date, fitbit_user_id):
    fitbit_activities_url = Fitbit_BASE_URL + f'/1/user/{fitbit_user_id}/activities/list.json?'
    fitbit_activities_url += f'afterDate={start_date}'
    fitbit_activities_url += '&sort=asc'
    fitbit_activities_url += '&limit=100'
    fitbit_activities_url += '&offset=0'
    response = requests.get(fitbit_activities_url, headers=headers)
    return response


def get_data_from_fitbit(
        db: Session,
        user_id: int
):
    # Getting fitibit user ID
    fitbit_user_id = crud.get_fitbit_user_id(db, user_id)
    if not fitbit_user_id:
        raise HTTPException(status_code=404, detail='There is no fitbit account connected to this user')

    # Getting fitbit token to get data from fitbit APIs
    fitbit_token = crud.get_fitbit_token_by_user_id(db, user_id)
    if not fitbit_token:
        raise HTTPException(status_code=403, detail="Server failed to get access to the Fitbit API")

    # Updating the fitbit token to make sure it's not expired
    new_fitbit_token = refresh_fitbit_token(fitbit_token)
    crud.add_fitbit_token(db, user_id, new_fitbit_token.access_token, new_fitbit_token.refresh_token)

    # setting up the required headers for fitbit APIs
    fitbit_token_str = fitbit_token.access_token
    headers = {
        'Authorization': f'Bearer {fitbit_token_str}',
    }

    # getting data for the last 70 days
    start_date = date.today() - timedelta(days=70)
    start_date_formatted = start_date.strftime('%Y-%m-%d')
    activities_response = get_fitbit_activities(headers, start_date_formatted, fitbit_user_id)

    if activities_response.status_code == 200:
        return activities_response.json()['activities']
    elif activities_response.status_code == 401:
        raise HTTPException(status_code=403, detail="Server failed to get access to the Fitbit API")
    else:
        raise HTTPException(status_code=activities_response.status_code, detail=activities_response.text)


def update_fitbit_data(db, user_id):
    activities = get_data_from_fitbit(db, user_id)
    crud.add_fitbit_activities(db, user_id, activities)
