import requests
from fastapi import HTTPException
from database import crud
from datetime import date, timedelta

FITBIT_CLIENT_ID = '23PDRW'
FITBIT_CLIENT_SECRET = '5cff99a1510ed622f0abee34f0e68997'
PKCE_CODE_VERIFIER = '0n5r552d051q3e4l6a3t0x45224b5d4r3g4d2b0u3a2m012g6g4m6q3n4c5s0x1z5u42316v65465y260y4j0u0s0y6o261w0y5t1p66374a194f6m3m522u6x090k0x'
FITBIT_GET_TOKEN_URL = 'https://api.fitbit.com/oauth2/token'


def get_fitbit_token(fitbit_code):
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
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


def refresh_fitbit_token(fitbit_token):
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
        return response.json()
    else:
        raise HTTPException(status_code=403, detail="Server failed to get access to the Fitbit API")


def get_data_from_fitbit(db, user_id):
    fitbit_token = crud.get_fitbit_token_by_user_id(db, user_id)
    if not fitbit_token:
        raise HTTPException(status_code=401, detail='Token not found')

    fitbit_user_id = crud.get_fitbit_user_id(db, user_id)
    if not fitbit_user_id:
        raise HTTPException(status_code=404, detail='There is no fitbit account connected to this user')

    fitbit_token_str = fitbit_token.access_token
    headers = {
        'Authorization': f'Bearer {fitbit_token_str}',
    }

    start_date = date.today() - timedelta(days=70)
    start_date_formatted = start_date.strftime('%Y-%m-%d')
    user_profile_url = f'https://api.fitbit.com/1/user/{fitbit_user_id}/activities/list.json?'
    user_profile_url += f'afterDate={start_date_formatted}'
    user_profile_url += '&sort=asc'
    user_profile_url += '&limit=100'
    user_profile_url += '&offset=0'
    response = requests.get(user_profile_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        response_json = refresh_fitbit_token(fitbit_token)
        try:
            crud.add_fitbit_token(db, user_id, response_json.access_token, response_json.refresh_token)
        except:
            raise HTTPException(status_code=403, detail="Server failed to get access to the Fitbit API")
        return response_json
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)
