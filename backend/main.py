from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from database.init import get_db, Base, engine
from database import schemas, crud
from sqlalchemy.orm import Session

from utils import responses, password_utils, authentication_utils, data_utils

FITBIT_AUTHORIZATION_URL = 'https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=23PDRW&scope=activity+cardio_fitness+electrocardiogram+heartrate+location+nutrition+oxygen_saturation+profile+respiratory_rate+settings+sleep+social+temperature+weight&code_challenge=lMNXGvUcuN9QrksqDqnUpS4YaUhIWzaTNH3KJEpV_jA&code_challenge_method=S256&state='

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
def on_startup():
    """
    Function executed on application startup.
    This function creates all database tables defined in the Base metadata binding to the engine.
    """
    Base.metadata.create_all(bind=engine)


@app.post("/register/")
async def register(
        data: schemas.RegisterSchema,
        db: Session = Depends(get_db)
) -> responses.LoginResponseSchema:
    new_user = schemas.UserSchema(**data.dict())
    if crud.get_user_by_username(db, new_user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if crud.get_user_by_email(db, new_user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        db_user = crud.add_user(db, new_user)
        encrypted_password = password_utils.encrypt_password(data.password)
        crud.set_user_password(db, db_user.id, encrypted_password)
        crud.add_user_information(db, db_user.id)
        token = crud.add_token(db, db_user.id)
        return responses.LoginResponseSchema.from_orm(token)
    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid data")


@app.post("/login/")
async def login(
        data: schemas.LoginSchema,
        db: Session = Depends(get_db)
) -> responses.LoginResponseSchema:
    user = crud.get_user_by_username(db, data.username)
    if user and password_utils.check_password(data.password, crud.get_user_password(db, user.id)):
        token = crud.add_token(db, user.id)
        return responses.LoginResponseSchema.from_orm(token)
    raise HTTPException(status_code=400, detail="Invalid credentials")


@app.get("/profile/")
async def get_profile(
        request: Request,
        db: Session = Depends(get_db)
) -> responses.UserProfileResponseSchema:
    current_user = authentication_utils.get_current_user(request, db)
    user_information = crud.get_user_information_by_user_id(db, current_user.id)
    if not user_information:
        raise HTTPException(status_code=404, detail="User data not found")
    response = responses.UserProfileResponseSchema.from_orm(current_user)
    response.set_user_information(user_information)
    return response


@app.put("/profile/")
async def edit_profile(
        request: Request,
        data: schemas.UserInformationSchema,
        db: Session = Depends(get_db)
):
    current_user = authentication_utils.get_current_user(request, db)
    user_information = crud.edit_user_information(db, current_user.id, data)
    response = responses.UserProfileResponseSchema.from_orm(current_user)
    response.set_user_information(user_information)
    return response


@app.get("/home/")
async def home(
        request: Request,
        db: Session = Depends(get_db)
):
    try:
        current_user = authentication_utils.get_current_user(request, db)
        return "Authorized"
    except:
        return "Not authorized"


@app.get("/explore/")
async def explore(
        request: Request,
        db: Session = Depends(get_db)
):
    try:
        current_user = authentication_utils.get_current_user(request, db)
        return "Authorized"
    except:
        return "Not authorized"


@app.get("/about-us/")
async def about_us(
        request: Request,
        db: Session = Depends(get_db)
):
    try:
        current_user = authentication_utils.get_current_user(request, db)
        return "Authorized"
    except:
        return "Not authorized"


@app.get("/mydata/")
async def mydata(
        request: Request,
        db: Session = Depends(get_db)
):
    user = authentication_utils.get_current_user(request, db)
    fitbit_token = crud.get_fitbit_token_by_user_id(db, user.id)
    if not fitbit_token:
        raise HTTPException(status_code=403, detail="Server failed to get access to the Fitbit API")
    
    user_data = data_utils.get_data_from_fitbit(db, user.id)
    return user_data


@app.get("/fitbit-authenticate")
async def fitbit_authenticate(
        request: Request,
        db: Session = Depends(get_db)
):
    fitbit_code = request.query_params.get('code')
    user_token = request.query_params.get('state')
    user = authentication_utils.get_current_user_by_token(user_token, db)
    fitbit_token_response = data_utils.get_fitbit_token(fitbit_code)
    crud.add_fitbit_token(db, user.id, fitbit_token_response['access_token'], fitbit_token_response['refresh_token'])
    return Response(status_code=200)
