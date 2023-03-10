import json
import os
import sys
import logging

from datetime import datetime, timedelta
from typing import List, Union

from fastapi import Depends, FastAPI, HTTPException, Request, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from jose import JWTError, jwt
import jwt as jwt2

from passlib.context import CryptContext
from pydantic import BaseModel
from authlib.integrations.starlette_client import OAuth, OAuthError

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

well_known_json = []
well_known_jwks = []

with open('./static/.well-known/openid-configuration.json') as f:
    well_known_json = json.load(f)

with open('./static/.well-known/jwks') as f:
    well_known_jwks = json.load(f)

# to get a string like this run:
# openssl rand -hex 32
# put this into doppler with the name "JWT_SECRET_KEY"
try:
    SECRET_KEY = os.environ['JWT_SECRET_KEY']
except Exception:
    print("No JWT_SECRET_KEY found in the environment. Did you add it to your doppler?")
    exit()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# to get a hashed password in python for the example user
# python generate_password_hash.py <your-password>
# save this to doppler as EXAMPLE_USER_HASHED_PASSWORD
try:
    hashed_dev_password = os.environ['EXAMPLE_USER_HASHED_PASSWORD']
except Exception:
    print("No EXAMPLE_USER_HASHED_PASSWORD found in environment. Add string to doppler")
    print("by running python generate_password_hash.py <your-password>")
    exit()

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": hashed_dev_password,
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None
    scopes: List[str] = []


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token",
                                scopes={"me": "Read information about the current user.",
                                "items": "Read items."})

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: User = Security(get_current_user, scopes=["me"])
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.get("/.well-known/openid-configuration.json")
async def openid_configration():
    return well_known_json

@app.get("/.well-known/jwks")
async def get_jwks_json():
    return well_known_jwks

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]

@app.get("/")
async def home():
    return {}

@app.post("/read-jwt-token")
async def read_jwt_token(jwt_token: Request):
    token = await jwt_token.body()
    logger.info(token)
    decoded_token = jwt2.decode(token, options={"verify_signature": False})
    logger.info(decoded_token)
    return {}