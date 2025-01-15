from pydantic import BaseModel
from enum import Enum


class AuthorizationType(Enum):
    login = "login"
    register = "register"


class RegisterData(BaseModel):
    email: str
    password: str


class LoginData(BaseModel):
    email: str
    password: str


class AuthenticationData(BaseModel):
    type: AuthorizationType
    data: RegisterData | LoginData


class Token(BaseModel):
    access_token: str
    refresh_token: str
