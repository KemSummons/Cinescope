from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class CreateMovieRequest(BaseModel):
    name: str = Field(min_length=1)
    imageUrl: Optional[str] = None
    price: int = Field(ge=1, le=1000)
    description: str = Field(min_length=1)
    location: Literal["MSK", "SPB"]
    published: bool
    genreId: int = Field(ge=1, le=10)


class GenreData(BaseModel):
    name: str = Field(min_length=1)


class CreateMovieResponse(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=1)
    price: int = Field(ge=1, le=1000)
    description: str = Field(min_length=1)
    imageUrl: Optional[str] = None
    location: Literal["MSK", "SPB"]
    published: bool
    genreId: int = Field(ge=1, le=10)
    genre: GenreData
    createdAt: datetime
    rating: int = Field(ge=0)


class UserData(BaseModel):
    fullName: str = Field(min_length=1)


class ReviewData(BaseModel):
    userId: str
    rating: int = Field(ge=0)
    text: str = Field(min_length=1)
    createdAt: datetime
    user: UserData


class GetOneMovieResponse(CreateMovieResponse):
    reviews: list[ReviewData]


class GetAllMoviesResponse(BaseModel):
    movies: list[CreateMovieResponse]
    count: int
    page: int
    pageSize: int
    pageCount: int