import pytest
import requests

from clients.api_manager import ApiManager
from constants import BASE_URL
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator

@pytest.fixture(scope="function")
def test_user():
    """
    Фикстура для генерации случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": ["USER"]
    }

@pytest.fixture(scope="function")
def test_movie():
    """
    Фикстура для генерации случайного фильма для тестов.
    """
    random_movie = DataGenerator.generate_random_movie()
    return random_movie


@pytest.fixture(scope="function")
def update_movie_data():
    """
    Фикстура с данными для обновления информации о фильме
    """
    update_data = DataGenerator.generate_random_movie()
    return {
        "name": update_data["name"],
        "price": update_data["price"],
        "genreId": update_data["genreId"]
    }

@pytest.fixture(scope='function')
def super_admin_data(session):
    """
    Фикстура для админских кредов для создания, удаления и обновления информации о фильмах
    """
    yield {
        "username": "api1@gmail.com",
        "password": "asdqwe123Q"
    }
    session.headers.pop("Authorization", None)

@pytest.fixture(scope="function")
def create_new_movie(api_manager: ApiManager, super_admin_data, test_movie):
    """
    Фикстура для получения админских прав и создание нового фильма
    """
    api_manager.auth_api.authenticate_user(super_admin_data)
    create_response = api_manager.movie_api.create_movie(test_movie, expected_status=201)
    create_response_data = create_response.json()
    return create_response_data


@pytest.fixture(scope="function")
def registered_user(api_manager: ApiManager, test_user):
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    """
    response = api_manager.auth_api.register_user(test_user, expected_status=201)
    response_data = response.json()
    registered_user = test_user.copy()
    registered_user["id"] = response_data["id"]
    return registered_user

# @pytest.fixture(scope="session")

@pytest.fixture(scope="session")
def requester(session):
    """
    Фикстура для создания экземпляра CustomRequester.
    """
    return CustomRequester(session=session, base_url=BASE_URL)

@pytest.fixture(scope='session')
def session():
    """
    Фикстура для создания HTTP-сессии.
    """
    http_session = requests.Session()
    yield http_session
    http_session.close()

@pytest.fixture(scope="session")
def api_manager(session):
    """
    Фикстура для создания экземпляра ApiManager.
    """
    return ApiManager(session, BASE_URL)
