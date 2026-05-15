import datetime
import uuid
from constants import Roles
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterUserRequest(BaseModel):
    email: EmailStr
    fullName: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=20)
    passwordRepeat: str = Field(
        min_length=1,
        max_length=20,
        description="passwordRepeat должен полностью совпадать с полем password"
    )

    @field_validator("passwordRepeat")
    def check_password_repeat(cls, value: str, info) -> str:
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return value


class RegisterUserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    fullName: str = Field(min_length=1, max_length=100)
    verified: bool
    banned: bool
    roles: list[Roles]
    createdAt: datetime.datetime


class UserData(BaseModel):
    id: uuid.UUID
    email: EmailStr
    fullName: str = Field(min_length=1, max_length=100)
    roles: list[Roles]


class LoginUserResponse(BaseModel):
    user: UserData
    accessToken: str = Field(min_length=20)
    refreshToken: str = Field(min_length=20)
    expiresIn: int

class LoginUserRequest(BaseModel):
    email: str
    password: str