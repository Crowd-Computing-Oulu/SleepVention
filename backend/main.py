from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from fastapi import Body

from database.init import get_db, Base, engine
from database import schemas, crud
from sqlalchemy.orm import Session

from utils import responses, password_utils, authentication_utils, data_utils, study_utils, file_utils

FITBIT_AUTHORIZATION_URL = 'https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=23PDRW&scope=activity+cardio_fitness+electrocardiogram+heartrate+location+nutrition+oxygen_saturation+profile+respiratory_rate+settings+sleep+social+temperature+weight&code_challenge=lMNXGvUcuN9QrksqDqnUpS4YaUhIWzaTNH3KJEpV_jA&code_challenge_method=S256&state='

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount the 'css' directory to serve CSS files
app.mount("/css", StaticFiles(directory="../frontend/css"), name="css")

# Mount the 'images' directory to serve image files
app.mount("/images", StaticFiles(directory="../frontend/images"), name="images")

# Mount the 'scripts' directory to serve JavaScript files
app.mount("/scripts", StaticFiles(directory="../frontend/scripts"), name="scripts")

# Set up Jinja2 templates directory for HTML files
templates = Jinja2Templates(directory="../frontend/html")


# Serve the main HTML file
@app.api_route("/", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"], response_class=HTMLResponse)
async def get_root_html(request: Request):
    return templates.TemplateResponse("homepage.html", {"request": request})


@app.get("/homepage/", response_class=HTMLResponse)
async def get_homepage_html(request: Request):
    return templates.TemplateResponse("homepage.html", {"request": request})


@app.get("/about_us/", response_class=HTMLResponse)
async def get_about_us_html(request: Request):
    return templates.TemplateResponse("about_us.html", {"request": request})


@app.get("/create_study/", response_class=HTMLResponse)
async def get_create_study_html(request: Request):
    return templates.TemplateResponse("create_study.html", {"request": request})


@app.get("/edit_profile/", response_class=HTMLResponse)
async def get_edit_profile_html(request: Request):
    return templates.TemplateResponse("edit_profile.html", {"request": request})


@app.get("/explore/", response_class=HTMLResponse)
async def get_explore_html(request: Request):
    return templates.TemplateResponse("explore.html", {"request": request})


@app.get("/invite_user/", response_class=HTMLResponse)
async def get_invite_user_html(request: Request):
    return templates.TemplateResponse("invite_user.html", {"request": request})


@app.get("/login/", response_class=HTMLResponse)
async def get_login_html(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/mydata/", response_class=HTMLResponse)
async def get_mydata_html(request: Request):
    return templates.TemplateResponse("mydata.html", {"request": request})


@app.get("/mystudies/", response_class=HTMLResponse)
async def get_mystudies_html(request: Request):
    return templates.TemplateResponse("mystudies.html", {"request": request})


@app.get("/profile/", response_class=HTMLResponse)
async def get_profile_html(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})


@app.get("/register/", response_class=HTMLResponse)
async def get_register_html(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/study/", response_class=HTMLResponse)
async def get_study_html(request: Request):
    return templates.TemplateResponse("study.html", {"request": request})


@app.on_event("startup")
def on_startup():
    """
    Function executed on application startup.
    This function creates all database tables defined in the Base metadata binding to the engine.
    """
    Base.metadata.create_all(bind=engine)


@app.post("/register/")
async def register(
        request: Request,
        db: Session = Depends(get_db)
) -> responses.LoginResponseSchema:
    try:
        data = await request.json()
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

    except Exception as e:
        raise HTTPException(status_code=400, detail=e)


@app.post("/login/")
async def login(
        request: Request,
        db: Session = Depends(get_db)
):
    try:
        data = await request.json()
        user = crud.get_user_by_username(db, data["username"])
        if user and password_utils.check_password(data["password"], crud.get_user_password(db, user.id)):
            token = crud.add_token(db, user.id)
            return responses.LoginResponseSchema.from_orm(token)

        raise HTTPException(status_code=400, detail="Invalid credentials")

    except Exception as e:
        raise HTTPException(status_code=400, detail=e)


@app.get("/get_profile/")
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
        db: Session = Depends(get_db)
):
    try:
        data = await request.json()
        current_user = authentication_utils.get_current_user(request, db)
        user_information = crud.edit_user_information(db, current_user.id, data)
        response = responses.UserProfileResponseSchema.from_orm(current_user)
        response.set_user_information(user_information)
        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=e)


@app.get("/get_home/")
async def home(
        request: Request,
        db: Session = Depends(get_db)
):
    try:
        current_user = authentication_utils.get_current_user(request, db)
        return "Authorized"
    except:
        return "Not authorized"


@app.get("/get_explore/")
async def explore(
        request: Request,
        db: Session = Depends(get_db)
):
    try:
        user = authentication_utils.get_current_user(request, db)
        sleep_logs = []
        average_sleep = crud.get_average_sleep_data(db)

        # Getting sleep data from database
        db_sleep_logs = crud.get_fitbit_sleep_logs(db, user.id)
        for sleep_log in db_sleep_logs:
            sleep_logs.append(responses.FitbitSleepResponseSchema.from_orm(sleep_log))

        response = {
            'logs': sleep_logs,
            'average': average_sleep
        }
        return response

    except:
        return "Not authorized"


@app.get("/get_about_us/")
async def about_us(
        request: Request,
        db: Session = Depends(get_db)
):
    try:
        current_user = authentication_utils.get_current_user(request, db)
        return "Authorized"
    except:
        return "Not authorized"


@app.get("/get_mydata/")
async def mydata(
        request: Request,
        db: Session = Depends(get_db)
):
    # Get current user
    user = authentication_utils.get_current_user(request, db)

    # Update data tables
    data_utils.update_fitbit_data(db, user.id)
    print(user.id)

    response = {'activities': {}, 'heartrate': {}, 'sleep': {}, 'sleep_levels': {}, 'files': []}

    # Getting activity data from database
    fitbit_activities = crud.get_fitbit_activities(db, user.id)
    for activity in fitbit_activities:
        # Grouping activities based on their date
        if activity.date not in response['activities']:
            response['activities'][activity.date] = []
        response['activities'][activity.date].append(responses.FitbitActivityResponseSchema.from_orm(activity))

    # Getting heartrate data from database
    heartrate_logs = crud.get_fitbit_heartrate_logs(db, user.id)
    for hr_log in heartrate_logs:
        response['heartrate'][hr_log.date] = [responses.FitbitHeartrateResponseSchema.from_orm(hr_log)]

    # Getting sleep data from database
    sleep_logs = crud.get_fitbit_sleep_logs(db, user.id)
    for sleep_log in sleep_logs:
        new_sleep_obj = responses.FitbitSleepResponseSchema.from_orm(sleep_log)

        response['sleep_levels'][sleep_log.date] = []
        sleep_levels = crud.get_sleep_levels_by_sleep_id(db, sleep_log.id)
        for sleep_level in sleep_levels:
            sleep_level_obj = responses.FitbitSleepLevelResponseSchema.from_orm(sleep_level)
            response['sleep_levels'][sleep_log.date].append(sleep_level_obj)

        response['sleep'][sleep_log.date] = [new_sleep_obj]

    # Getting user uploaded data files from database
    data_files = crud.get_data_files(db, user.id)
    for f in data_files:
        response['files'].append(schemas.DataFileUploadSchema.from_orm(f))

    return response


@app.get("/fitbit-authenticate")
async def fitbit_authenticate(
        request: Request,
        db: Session = Depends(get_db)
):
    fitbit_code = request.query_params.get('code')
    user_token = request.query_params.get('state')
    user = authentication_utils.get_current_user_by_token(user_token, db)
    code_verifier = crud.get_fitbit_code_verifier(db, user.id)
    fitbit_token = data_utils.get_fitbit_token(fitbit_code, code_verifier)
    crud.add_fitbit_token(db, user.id, fitbit_token.access_token, fitbit_token.refresh_token)
    return Response(status_code=200)


@app.get("/fitbit_authenticating_url")
async def get_fitbit_authenticate(
        request: Request,
        db: Session = Depends(get_db)
):
    # Get current user
    user = authentication_utils.get_current_user(request, db)
    user_token = authentication_utils.get_token(request)
    auth_url, code_verifier = data_utils.generate_fitbit_auth_url(user_token)
    crud.add_fitbit_code_verifier(db, user.id, code_verifier)
    return auth_url


@app.post("/data_file/")
async def upload_file(
        request: Request,
        db: Session = Depends(get_db)
):
    try:
        data = await request.json()
        # Get current user
        user = authentication_utils.get_current_user(request, db)
        print(data.file_name, data.file_content)
        crud.add_data_file(db, user.id, data)

    except Exception as e:
        raise HTTPException(status_code=400, detail=e)



@app.get("/get_data_privacy/")
async def data_privacy(
        request: Request,
        db: Session = Depends(get_db)
) -> responses.DataPrivacyResponseSchema:
    # Get current user
    user = authentication_utils.get_current_user(request, db)

    data_privacy_db = crud.get_data_privacy_settings(db, user.id)
    response = responses.DataPrivacyResponseSchema.from_orm(data_privacy_db)
    return response


@app.put("/data_privacy/")
async def edit_data_privacy(
        request: Request,
        db: Session = Depends(get_db)
) -> responses.DataPrivacyResponseSchema:
    try:
        data = await request.json()
        # Get current user
        user = authentication_utils.get_current_user(request, db)

        new_data_privacy = crud.edit_data_privacy_settings(db, user.id, data)
        response = responses.DataPrivacyResponseSchema.from_orm(new_data_privacy)
        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=e)


@app.post("/study/")
async def create_study(
        request: Request,
        db: Session = Depends(get_db)
):
    try:
        data = await request.json()
        user = authentication_utils.get_current_user(request, db)
        crud.add_study(db, user.id, data)

    except Exception as e:
        raise HTTPException(status_code=400, detail=e)


@app.get("/get_own_studies/")
async def get_own_studies(
        request: Request,
        db: Session = Depends(get_db)
) -> list[responses.StudyResponseSchema]:
    user = authentication_utils.get_current_user(request, db)

    response = []
    studies = crud.get_own_studies(db, user.id)
    for study in studies:
        response.append(responses.StudyResponseSchema.from_orm(study))

    return response


@app.get("/get_participated_studies/")
async def get_participated_studies(
        request: Request,
        db: Session = Depends(get_db)
) -> list[responses.StudyResponseSchema]:
    user = authentication_utils.get_current_user(request, db)

    response = []
    studies = user.participated_studies
    for study in studies:
        response.append(responses.StudyResponseSchema.from_orm(study))

    return response


@app.get("/get_study/{study_id}/")
async def get_study(
        study_id: int,
        request: Request,
        db: Session = Depends(get_db)
) -> responses.StudyResponseSchema:
    user = authentication_utils.get_current_user(request, db)

    retrieved_study = crud.get_study_by_id(db, study_id)
    if not retrieved_study:
        raise HTTPException(status_code=404, detail="Study not found")

    response = responses.StudyResponseSchema.from_orm(retrieved_study)
    response.participants_number = len(retrieved_study.participants)
    user_role = study_utils.get_user_study_relation(db, retrieved_study, user)
    if retrieved_study.type == 'private' and user_role == 'visitor':
        raise HTTPException(status_code=403, detail="You don't have access to this study")
    response.user_relation = user_role
    return response


@app.delete("/study/{study_id}/")
async def delete_study(
        request: Request,
        study_id: int,
        db: Session = Depends(get_db)
):
    user = authentication_utils.get_current_user(request, db)
    crud.delete_study(db, study_id)
    return {"detail": "Study deleted successfully"}


@app.post("/study/{study_id}/invite/")
async def invite_to_study(
        request: Request,
        study_id: int,
        db: Session = Depends(get_db)
):
    try:
        data = await request.json()
        user = authentication_utils.get_current_user(request, db)

        invited_user = crud.get_user_by_invitation(db, data)
        # Checking if a user with that information exists in the database
        if not invited_user:
            raise HTTPException(status_code=404, detail="The user with the provided username/email was not found")

        # Checking if the user is already participating in the study
        if crud.check_participant_in_study(db, invited_user.id, study_id):
            raise HTTPException(status_code=409, detail="The invited user is already in this study")

        invitation = crud.add_study_invitation(db, invited_user.id, study_id)
        # Checking if the user is already invited to the study
        if not invitation:
            raise HTTPException(status_code=409, detail="An invitation has already been sent to this user")

        return {"detail": "Invitation sent to the user"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=e)


@app.get("/get_invitations/")
async def get_invitations(
        request: Request,
        db: Session = Depends(get_db)
) -> list[responses.StudyResponseSchema]:
    user = authentication_utils.get_current_user(request, db)

    invitations = crud.get_user_invitations(db, user.id)
    response = []
    for invitation in invitations:
        invited_study = responses.StudyResponseSchema.from_orm(invitation.study)
        invited_study.participants_number = len(invitation.study.participants)
        response.append(invited_study)

    return response


@app.delete("/invitation/{study_id}/")
async def delete_invitation(
        request: Request,
        study_id: int,
        db: Session = Depends(get_db)
):
    user = authentication_utils.get_current_user(request, db)
    crud.delete_invitation(db, user.id, study_id)
    return {"detail": "Invitation was deleted successfully"}


@app.put("/invitation/{study_id}/")
async def accept_invitation(
        request: Request,
        study_id: int,
        db: Session = Depends(get_db)
):
    user = authentication_utils.get_current_user(request, db)
    db_result = crud.accept_invitation(db, user.id, study_id)
    if not db_result:
        raise HTTPException(status_code=409, detail="Invitation is already accepted")
    return {"detail": "Invitation was accepted successfully"}


@app.get("/get_study/{study_id}/data/csv/")
async def get_study_data_csv(
        request: Request,
        study_id: int,
        db: Session = Depends(get_db)
):
    user = authentication_utils.get_current_user(request, db)

    creator_access_to_study = authentication_utils.check_study_creator(user.id, study_id, db)
    if not creator_access_to_study:
        raise HTTPException(status_code=403, detail="You don't have access to this data")

    study = crud.get_study_by_id(db, study_id)
    participants_data = {}
    for i, participant in enumerate(study.participants):
        activities = crud.get_fitbit_activities(db, participant.id)
        activities_csv = file_utils.query_to_csv(activities)

        heartrate_logs = crud.get_fitbit_heartrate_logs(db, participant.id)
        hr_csv = file_utils.query_to_csv(heartrate_logs)

        sleep_logs = crud.get_fitbit_sleep_logs(db, participant.id)
        sleep_logs_csv = file_utils.query_to_csv(sleep_logs)

        sleep_levels = crud.get_sleep_levels_by_user_id(db, participant.id)
        sleep_levels_csv = file_utils.query_to_csv(sleep_levels)

        participant_zip_file = file_utils.create_zip_from_csvs(
            {
                'activities.csv': activities_csv,
                'heartrate.csv': hr_csv,
                'sleep.csv': sleep_logs_csv,
                'sleep_levels.csv': sleep_levels_csv
            }
        )

        file_name = 'user' + str(i+1) + '.zip'
        participants_data[file_name] = participant_zip_file

    response_zip_file = file_utils.create_zip_from_csvs(participants_data)

    # Return the ZIP file as a response
    return StreamingResponse(
        response_zip_file,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": "attachment; filename=data.zip"}
    )


@app.get("/get_studies/public/")
async def get_public_studies(
        request: Request,
        db: Session = Depends(get_db)
) -> list[responses.StudyResponseSchema]:

    public_studies = crud.get_public_studies(db)

    try:
        user = authentication_utils.get_current_user(request, db)
        public_studies = study_utils.remove_related_studies_from_study_list(public_studies, user)
    except:
        pass
    response = []
    for study in public_studies:
        response.append(responses.StudyResponseSchema.from_orm(study))

    return response

