from datetime import date, timedelta, datetime

import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session
from database import crud, schemas, tables
import json
import base64
import hashlib
import os

from utils import password_utils

FITBIT_CLIENT_ID = '23Q77F'
FITBIT_CLIENT_SECRET = '38f27b1c182a2e5808e9a6e032221c20'
FITBIT_GET_TOKEN_URL = 'https://api.fitbit.com/oauth2/token'
Fitbit_BASE_URL = 'https://api.fitbit.com'
REDIRECT_URI = "http://127.0.0.1:8000/fitbit-authenticate"
FITBIT_SCOPES = "activity cardio_fitness electrocardiogram heartrate location nutrition oxygen_saturation profile respiratory_rate settings sleep social temperature weight"


def get_fitbit_token(fitbit_code, code_verifier) -> schemas.FitbitTokenSchema:
    client_credentials = f"{FITBIT_CLIENT_ID}:{FITBIT_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(client_credentials.encode()).decode()

    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'client_id': FITBIT_CLIENT_ID,
        'grant_type': 'authorization_code',
        'code': fitbit_code,
        'code_verifier': code_verifier
    }
    response = requests.post(FITBIT_GET_TOKEN_URL, headers=headers, data=data)
    if response.status_code == 200:
        fitbit_token = schemas.FitbitTokenSchema(**response.json())
        return fitbit_token
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


def refresh_fitbit_token(fitbit_token) -> schemas.FitbitTokenSchema:
    refresh_token_str = fitbit_token.refresh_token
    client_credentials = f"{FITBIT_CLIENT_ID}:{FITBIT_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(client_credentials.encode()).decode()

    headers = {
        'Authorization': f'Basic {encoded_credentials}',
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


def format_date_to_str(date_obj):
    return date_obj.strftime('%Y-%m-%d')


def get_fitbit_activities(headers, start_date):
    fitbit_activities_url = Fitbit_BASE_URL + f'/1/user/-/activities/list.json?'
    fitbit_activities_url += f'afterDate={start_date}'
    fitbit_activities_url += '&sort=asc'
    fitbit_activities_url += '&limit=100'
    fitbit_activities_url += '&offset=0'
    response = requests.get(fitbit_activities_url, headers=headers)
    return response


def get_fitbit_heartrate(headers, start_date):
    # Be careful that the maximum range is 1 year
    fitbit_heartrate_url = Fitbit_BASE_URL + f'/1/user/-/activities/heart/date/{start_date}/today.json'
    response = requests.get(fitbit_heartrate_url, headers=headers)
    return response


def get_fitbit_hrv(headers, start_date, db, user_id):
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
    get_more_hrv = False

    # Be careful that the maximum range is 30 days
    if date.today() - timedelta(days=29) > start_date_obj:
        end_date = start_date_obj + timedelta(days=29)
        end_date_str = format_date_to_str(end_date)
        fitbit_hrv_url = Fitbit_BASE_URL + f'/1/user/-/hrv/date/{start_date}/{end_date_str}.json'

        crud.save_fitbit_last_update(db, user_id, end_date_str, 'hrv')
        get_more_hrv = True
    else:
        fitbit_hrv_url = Fitbit_BASE_URL + f'/1/user/-/hrv/date/{start_date}/today.json'
        crud.save_fitbit_last_update(db, user_id, 'today', 'hrv')
    response = requests.get(fitbit_hrv_url, headers=headers)
    return response, get_more_hrv


def get_fitbit_sleep(headers, start_date):
    fitbit_sleep_url = Fitbit_BASE_URL + f'/1.2/user/-/sleep/list.json?'
    fitbit_sleep_url += f'afterDate={start_date}'
    fitbit_sleep_url += '&sort=asc'
    fitbit_sleep_url += '&limit=100'
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
        user_id: int,
        last_updates,
        get_only_hrv: bool = False
):
    # Getting fitbit user ID
    # fitbit_user_id = crud.get_fitbit_user_id(db, user_id)
    # if not fitbit_user_id:
    #     raise HTTPException(status_code=404, detail='There is no fitbit account connected to this user')

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

    # Getting Fitbit heartrate variability data
    hrv_start_date = format_date_to_str(last_updates.hrv)
    hrv_response, get_more_hrv = get_fitbit_hrv(headers, hrv_start_date, db, user_id)
    if get_only_hrv:
        print('hrv second request working')
        return hrv_response.json()['hrv']

    # Getting Fitbit activity data
    activity_start_date = format_date_to_str(last_updates.activity)
    activities_response = get_fitbit_activities(headers, activity_start_date)

    # Getting Fitbit heartrate data
    heartrate_start_date = format_date_to_str(last_updates.heart_rate)
    hr_response = get_fitbit_heartrate(headers, heartrate_start_date)

    # Getting Fitbit sleep data
    sleep_start_date = format_date_to_str(last_updates.sleep)
    sleep_response = get_fitbit_sleep(headers, sleep_start_date)

    # Since all the requests are to the same domain, we only check one of them
    # to see if there is an access problem
    if sleep_response.status_code == 200:
        return combine_fitbit_responses(activities_response, hr_response, hrv_response, sleep_response), get_more_hrv
    elif sleep_response.status_code == 401:
        raise HTTPException(status_code=403, detail="Server failed to get access to the Fitbit API")
    else:
        raise HTTPException(status_code=activities_response.status_code, detail=activities_response.text)


def update_fitbit_data(db, user_id):
    last_updates = crud.get_fitbit_last_updates(db, user_id)

    # getting updated data from Fitbit APIs
    fitbit_data, get_more_hrv = get_data_from_fitbit(db, user_id, last_updates)

    # Storing the updated data in database
    crud.add_fitbit_activities(db, user_id, fitbit_data['activities'])
    crud.add_fitbit_heartrate_logs(db, user_id, fitbit_data['heartrate'])
    crud.add_fitbit_hrv_logs(db, user_id, fitbit_data['hrv'])
    crud.add_fitbit_sleep_logs(db, user_id, fitbit_data['sleep'])

    # Making another request to get more hrv data (since hrv only gives data of max 30 days)
    if get_more_hrv:
        last_updates = crud.get_fitbit_last_updates(db, user_id)
        hrv_data_2 = get_data_from_fitbit(db, user_id, last_updates, True)
        crud.add_fitbit_hrv_logs(db, user_id, hrv_data_2)


def read_sleep_data_and_insert(json_file_path: str, session: Session):
    # Step 1: Read the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as file:
        sleep_data = json.load(file)

    # Step 3: Iterate over the JSON data to extract information
    user_count = 5
    for id1, nested_data in sleep_data.items():
        for id2, sleep_info in nested_data.items():
            # Extract date and sleep information
            for date, sleep_data in sleep_info.items():
                sleep_details = sleep_data.get("sleep", None)

                if sleep_details:
                    # Create a new user
                    username = f"User{user_count}"
                    email = f"abc{user_count}@gmail.com"
                    new_user = tables.Users(username=username, email=email)
                    session.add(new_user)
                    session.commit()  # Commit to get the user's ID
                    user_id = new_user.id

                    encrypted_password = password_utils.encrypt_password('111')
                    crud.set_user_password(session, user_id, encrypted_password)
                    crud.add_user_information(session, user_id)

                    crud.add_fitbit_sleep_logs(session, user_id, [sleep_details])

                    # Increment the user count for unique username
                    user_count += 1


def generate_pkce_pair():
    # Generate a random code_verifier (43-128 characters)
    code_verifier = base64.urlsafe_b64encode(os.urandom(64)).decode('utf-8').rstrip("=")

    # Create a SHA256 hash of the code_verifier
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip("=")

    return code_verifier, code_challenge


def generate_fitbit_auth_url(user_token):
    code_verifier, code_challenge = generate_pkce_pair()

    auth_url = (
        f"https://www.fitbit.com/oauth2/authorize?"
        f"response_type=code"
        f"&client_id={FITBIT_CLIENT_ID}"
        f"&scope={FITBIT_SCOPES}"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
        f"&state={user_token}"
        f"&prompt=login"
    )

    return auth_url, code_verifier
