import uuid
import datetime
from typing import Literal
from pydantic import BaseModel, Field, field_validator, EmailStr
from constants import Roles


class UserData(BaseModel):
    email: EmailStr
    fullName: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=20)
    passwordRepeat: str = Field(
        min_length=1,
        max_length=20,
        description="passwordRepeat должен полностью совпадать с полем password"
    )
    roles: list[Roles]
    verified: bool
    banned: bool

    @field_validator("passwordRepeat")
    def check_password_repeat(cls, value: str, info) -> str:
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return value


class CreateUserRequest(BaseModel):
    fullName: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=1, max_length=20)
    verified: bool
    banned: bool


class CreateUserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    fullName: str = Field(min_length=1, max_length=100)
    roles: list[Roles]
    verified: bool
    createdAt: datetime.datetime
    banned: bool


class GetAllUsersResponse(BaseModel):
    users: list[CreateUserResponse]
    count: int = Field(ge=0)
    page: int = Field(ge=1)
    pageSize: int = Field(ge=1)


class UpdateUserRequest(BaseModel):
    roles: list[Roles] | None = None
    verified: bool | None = None
    banned: bool | None = None


class UpdateUserResponse(BaseModel):
    id: uuid.UUID | None = None
    email: EmailStr
    fullName: str = Field(min_length=1, max_length=100)
    roles: list[Roles]
    verified: bool
    createdAt: datetime.datetime
    banned: bool


class GetUsersQueryParams(BaseModel):
    pageSize: int | None = Field(default=None, ge=1)
    page: int | None = Field(default=None, ge=1)
    roles: list[Roles] | None = None
    createdAt: Literal["asc", "desc"] | None = None
