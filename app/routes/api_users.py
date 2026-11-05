"""/api/users routes (Chapter 3: server/routes/user.routes.js + controllers/user.controller.js).

    GET    /api/users            list users           (public)
    POST   /api/users            sign up              (public)
"""
from fastapi import APIRouter

from app import user_service
from app.models.user import UserCreate, UserOut

# [BEGINNER] APIRouter is express.Router(): a group of routes that main.py mounts on the app.
router = APIRouter(prefix="/api/users", tags=["users"])


# [BEGINNER] The decorator line is the route (router.route('/api/users').get(...)), the
# function below it is the controller. response_model=list[UserOut] filters every user
# through UserOut, so hashed_password and salt are never sent.
@router.get("", response_model=list[UserOut])
async def list_users():
    return [UserOut.from_user(user) for user in await user_service.list_users()]


# [BEGINNER] `body: UserCreate` tells FastAPI to read the JSON body and validate it BEFORE this
# function runs. An invalid body never reaches it: the RequestValidationError handler in
# main.py answers 400 with every message, e.g. "Name is required. Please fill a valid ...".
@router.post("", status_code=201)
async def create(body: UserCreate):
    await user_service.create_user(body)
    return {"message": "Successfully signed up!"}
