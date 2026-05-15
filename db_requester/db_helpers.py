import datetime
from uuid import uuid4
from sqlalchemy.orm import Session
from db_models.user_db_model import UserDBModel
from db_models.movie_db_model import MovieDBModel
from models.movie_api_models import CreateMovieRequest


class DBHelper:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    """Класс с методами для работы с БД в тестах"""

    def create_test_user(self, user_data: dict) -> UserDBModel:
        """Создает тестового пользователя"""
        user = UserDBModel(**user_data)
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user

    def get_user_by_id(self, user_id: str):
        """Получает пользователя по ID"""
        return self.db_session.query(UserDBModel).filter(UserDBModel.id == user_id).first()

    def get_user_by_email(self, email: str):
        """Получает пользователя по email"""
        return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).first()

    def create_movie(self, movie_data: dict | CreateMovieRequest) -> MovieDBModel:
        """Создает новый фильм"""
        if isinstance(movie_data, CreateMovieRequest):
            movie_data = movie_data.model_dump()

        db_movie_data = {
            "name": movie_data["name"],
            "price": float(movie_data["price"]),
            "description": movie_data["description"],
            "image_url": movie_data.get("imageUrl") or movie_data.get("image_url"),
            "location": movie_data["location"],
            "published": movie_data["published"],
            "rating": float(movie_data.get("rating", 0)),
            "genre_id": movie_data.get("genreId") or movie_data.get("genre_id"),
            "created_at": movie_data.get("created_at", datetime.datetime.now()),
        }

        movie = MovieDBModel(**db_movie_data)
        self.db_session.add(movie)
        self.db_session.commit()
        self.db_session.refresh(movie)
        return movie

    def get_movie_by_name(self, name: str):
        """Получает фильм по названию"""
        return self.db_session.query(MovieDBModel).filter(MovieDBModel.name == name).first()

    def get_movie_by_id(self, movie_id: str):
        """Получает фильм по ID"""
        return self.db_session.query(MovieDBModel).filter(MovieDBModel.id == movie_id).first()

    def user_exists_by_email(self, email: str) -> bool:
        """Проверяет существование пользователя по email"""
        return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).count() > 0

    def delete_user(self, user: UserDBModel):
        """Удаляет пользователя"""
        self.db_session.delete(user)
        self.db_session.commit()

    def cleanup_test_data(self, objects_to_delete: list):
        """Очищает тестовые данные"""
        for obj in objects_to_delete:
            if obj:
                self.db_session.delete(obj)
        self.db_session.commit()

