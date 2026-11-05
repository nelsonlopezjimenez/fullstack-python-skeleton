"""/api/users routes (Chapter 3: server/routes/user.routes.js + controllers/user.controller.js).

    GET    /api/users             list users           (public)
    POST   /api/users             sign up              (public)
    GET    /api/users/{user_id}   read one user        (signed in)
    PATCH  /api/users/{user_id}   update own profile   (signed in + owner)
    DELETE /api/users/{user_id}   delete own account   (signed in + owner)
"""
from fastapi import APIRouter, Depends

from app import user_service
from app.auth import has_authorization, user_by_id
from app.models.user import User, UserCreate, UserOut, UserUpdate

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


# [BEGINNER] Chapter 3 listed the middleware in the route:
#   .get(authCtrl.requireSignin, userCtrl.userByID, userCtrl.read)
# Here the handler ASKS for what it needs: `profile: User = Depends(user_by_id)`. FastAPI runs
# user_by_id, which itself depends on require_signin (see app/auth.py), so the order is the same:
# token (401) → load user (400 bad id / 404) → handler.
@router.get("/{user_id}", response_model=UserOut)
async def read(profile: User = Depends(user_by_id)):
    return UserOut.from_user(profile)


# has_authorization adds the owner check (403) on top of user_by_id.
# [ADVANCED] PATCH, as in Chapter 3: the client sends only the fields that change.
@router.patch("/{user_id}", response_model=UserOut)
async def update(body: UserUpdate, profile: User = Depends(has_authorization)):
    return UserOut.from_user(await user_service.update_user(profile, body))


@router.delete("/{user_id}", response_model=UserOut)
async def remove(profile: User = Depends(has_authorization)):
    await profile.delete()  # Mongoose: user.deleteOne()
    return UserOut.from_user(profile)
