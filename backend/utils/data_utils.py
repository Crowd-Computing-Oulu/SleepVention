import requests
from fastapi import HTTPException


def get_fitbit_token():
    return 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1BEUlciLCJzdWIiOiJDNFFKRzgiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJlY2cgcnNldCByb3h5IHJwcm8gcm51dCByc2xlIHJjZiByYWN0IHJsb2MgcnJlcyByd2VpIHJociBydGVtIiwiZXhwIjoxNzE5MjUwODc1LCJpYXQiOjE3MTkyMjIwNzV9.Se8dg7z5ouI7wFvXMIZUP3SDctfj0yvV6joF9D48cdA'


def get_data_from_fitbit():
    token = get_fitbit_token()
    headers = {
        'Authorization': f'Bearer {token}',
    }

    # Get user profile
    user_profile_url = 'https://api.fitbit.com/1/user/-/activities/date/2024-06-24.json'
    response = requests.get(user_profile_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)
