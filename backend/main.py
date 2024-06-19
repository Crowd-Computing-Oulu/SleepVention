from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from database.init import get_db, Base, engine
from database import schemas, crud
from sqlalchemy.orm import Session

from utils import responses, password_utils, authentication_utils

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

