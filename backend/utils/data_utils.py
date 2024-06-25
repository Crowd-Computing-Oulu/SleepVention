import requests
from fastapi import HTTPException
from database import crud

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


def get_data_from_fitbit(db, user_id):
    fitbit_token = crud.get_fitbit_token_by_user_id(db, user_id)
    if not fitbit_token:
        raise HTTPException(status_code=401, detail='Token not found')
    fitbit_token_str = fitbit_token.access_token
    headers = {
        'Authorization': f'Bearer {fitbit_token_str}',
    }

    # Get user profile
    user_profile_url = 'https://api.fitbit.com/1/user/-/activities/date/2024-06-24.json'
    response = requests.get(user_profile_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)
