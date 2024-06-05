from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from database.init import get_db, Base, engine
from database import schemas, crud
from sqlalchemy.orm import Session
from utils.password_utils import encrypt_password

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
):
    new_user = schemas.UserSchema(**data.dict())
    if crud.get_user_by_username(db, new_user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if crud.get_user_by_email(db, new_user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        db_user = crud.add_user(db, new_user)
        encrypted_password = encrypt_password(data.password)
        crud.set_user_password(db, db_user.id, encrypted_password)
        crud.add_user_information(db, db_user.id)
        return {"message": "User registered successfully"}
    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid data")


@app.post("/login/")
async def login(
        data: schemas.LoginSchema,
        db: Session = Depends(get_db)
):
    print(data.username, data.password)
    return {"msg": "Hello "}


@app.get("/profile/")
async def profile():
    return {
        "sub": "testuser",
        "username": "testuser",
        "email": "testuser@example.com",
        "nationality": "Exampleland",
        "birthdate": "2000-01-01",
        "gender": "Other",
        "height": 170.5,
        "weight": 70.0
    }
    # raise HTTPException(status_code=400, detail="Invalid credentials")


@app.put("/profile/")
async def profile():
    return {"msg": "Hello "}
