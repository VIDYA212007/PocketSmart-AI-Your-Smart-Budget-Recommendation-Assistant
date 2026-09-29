from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: bool = False


class UserCreate(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    password: str


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None