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
    fitbit_activities_url += '&limit=10'  # The limit should be changed to 100
    fitbit_activities_url += '&offset=0'
    response = requests.get(fitbit_activities_url, headers=headers)
    return response


def get_fitbit_heartrate(headers, start_date, fitbit_user_id):
    fitbit_heartrate_url = Fitbit_BASE_URL + f'/1/user/{fitbit_user_id}/activities/heart/date/{start_date}/today.json'
    response = requests.get(fitbit_heartrate_url, headers=headers)
    return response


def get_fitbit_hrv(headers, start_date, fitbit_user_id):
    # fitbit_hrv_url = Fitbit_BASE_URL + f'/1/user/{fitbit_user_id}/hrv/date/{start_date}/today.json'

    # The following line is for testing purpose, it should be replaced by the above line
    fitbit_hrv_url = Fitbit_BASE_URL + f'/1/user/{fitbit_user_id}/hrv/date/{start_date}/2023-10-30.json'
    response = requests.get(fitbit_hrv_url, headers=headers)
    return response


def get_fitbit_sleep(headers, start_date, fitbit_user_id):
    fitbit_sleep_url = Fitbit_BASE_URL + f'/1.2/user/{fitbit_user_id}/sleep/list.json?'
    fitbit_sleep_url += f'afterDate={start_date}'
    fitbit_sleep_url += '&sort=asc'
    fitbit_sleep_url += '&limit=10'  # The limit should be changed to 100
    fitbit_sleep_url += '&offset=0'
    response = requests.get(fitbit_sleep_url, headers=headers)
    return response


def combine_fitbit_responses(activities_response, heartrate_response, hrv_response, sleep_response):
    return {
        'activities': activities_response.json()['activities'],
        'heartrate': heartrate_response.json()['activities-heart'],
        'hrv': hrv_response.json()['hrv'],
        'sleep': sleep_response.json()['sleep']
    }


def get_data_from_fitbit(
        db: Session,
        user_id: int
):
    # Getting fitbit user ID
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
        'Authorization': f'Bearer {fitbit_token_str}'
    }

    # Setting the start time for 30 days ago
    # start_date = date.today() - timedelta(days=30)
    # start_date_formatted = start_date.strftime('%Y-%m-%d')

    # I changed the dates for testing purpose
    start_date_formatted = '2023-10-10'

    # Getting Fitbit activity data
    activities_response = get_fitbit_activities(headers, start_date_formatted, fitbit_user_id)

    # Getting Fitbit heartrate data
    hr_response = get_fitbit_heartrate(headers, start_date_formatted, fitbit_user_id)

    # Getting Fitbit heartrate variability data
    hrv_response = get_fitbit_hrv(headers, start_date_formatted, fitbit_user_id)

    # Getting Fitbit sleep data
    sleep_response = get_fitbit_sleep(headers, start_date_formatted, fitbit_user_id)
    sjson = sleep_response.json()

    # Since all the requests are to the same domain, we only check one of them
    # to see if there is an access problem
    if activities_response.status_code == 200:
        return combine_fitbit_responses(activities_response, hr_response, hrv_response, sleep_response)
    elif activities_response.status_code == 401:
        raise HTTPException(status_code=403, detail="Server failed to get access to the Fitbit API")
    else:
        raise HTTPException(status_code=activities_response.status_code, detail=activities_response.text)


def update_fitbit_data(db, user_id):
    # getting updated data from Fitbit APIs
    fitbit_data = get_data_from_fitbit(db, user_id)

    # Storing the updated data in database
    crud.add_fitbit_activities(db, user_id, fitbit_data['activities'])
    crud.add_fitbit_heartrate_logs(db, user_id, fitbit_data['heartrate'])
    crud.add_fitbit_hrv_logs(db, user_id, fitbit_data['hrv'])
    crud.add_fitbit_sleep_logs(db, user_id, fitbit_data['sleep'])
