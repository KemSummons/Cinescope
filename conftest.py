import pytest
import requests
from clients.api_manager import ApiManager
from constants import BASE_URL, Roles, get_roles
from utils.data_generator import DataGenerator
from resources.user_creds import SuperAdminCreds
from user import User

@pytest.fixture(scope='function')
def user_factory():
    """
    Фикстура для генерации случайного пользователя для тестов с нужной ролью.
    """
    def create_user(role=Roles.USER):
        random_email = DataGenerator.generate_random_email()
        random_name = DataGenerator.generate_random_name()
        random_password = DataGenerator.generate_random_password()

        return {
            "email": random_email,
            "fullName": random_name,
            "password": random_password,
            "passwordRepeat": random_password,
            "roles": get_roles(role)
        }
    return create_user

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

@pytest.fixture(scope='session')
def super_admin_data(session):
    """
    Фикстура для админских кредов для создания, удаления и обновления информации о фильмах
    """
    yield {
        "username": SuperAdminCreds.USERNAME,
        "password": SuperAdminCreds.PASSWORD
    }
    session.headers.pop("Authorization", None)

@pytest.fixture(scope='session')
def authenticated_admin(api_manager: ApiManager, super_admin_data):
    api_manager.auth_api.authenticate_user(super_admin_data)
    return api_manager

@pytest.fixture(scope="function")
def create_new_movie(authenticated_admin, test_movie):
    """
    Фикстура для получения админских прав и создание нового фильма с teardown
    """
    create_response = authenticated_admin.movie_api.create_movie(test_movie, expected_status=201)
    create_response_data = create_response.json()
    yield create_response_data
    movie_id = create_response_data.get("id")
    if movie_id is not None:
        authenticated_admin.movie_api.delete_movie(movie_id, expected_status=200)

@pytest.fixture(scope="function")
def create_new_movie_without_teardown(authenticated_admin, test_movie):
    """
    Фикстура для получения админских прав и создание нового фильма без teardown
    """
    create_response = authenticated_admin.movie_api.create_movie(test_movie, expected_status=201)
    create_response_data = create_response.json()
    return create_response_data

@pytest.fixture(scope="function")
def registered_user(api_manager: ApiManager, user_factory):
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    """
    response = api_manager.auth_api.register_user(user_factory(Roles.USER.value), expected_status=201)
    response_data = response.json()
    registered_user = user_factory(Roles.USER.value).copy()
    registered_user["id"] = response_data["id"]
    return registered_user

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

@pytest.fixture
def user_session():
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session, base_url="https://auth.dev-cinescope.coconutqa.ru")
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()

@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session
    )

    super_admin.api.auth_api.authenticate_user(super_admin.creds)
    return super_admin

@pytest.fixture(scope="function")
def creation_user_factory(user_factory):
    def creation_user_data(role=Roles.USER):
        data = user_factory(role=role)
        updated_data = data.copy()
        updated_data.update({
            "verified": True,
            "banned": False
        })
        return updated_data

    return creation_user_data

@pytest.fixture(scope='function')
def create_common_user(user_session, super_admin, creation_user_factory):
    new_session = user_session()
    new_data = creation_user_factory().copy()
    common_user = User(
        new_data['email'],
        new_data['password'],
        new_data['roles'],
        new_session
    )

    response_data = super_admin.api.user_api.create_user(new_data)
    common_user.api.auth_api.authenticate_user(common_user.creds)

    yield common_user

    user_id = response_data.json()['id']
    if user_id is not None:
        super_admin.api.user_api.delete_user(user_id, expected_status=200)

@pytest.fixture(scope='function')
def create_admin_user(user_session, super_admin, creation_user_factory):
    new_session = user_session()
    new_data = creation_user_factory(role=Roles.ADMIN).copy()
    admin_user = User(
        new_data['email'],
        new_data['password'],
        new_data['roles'],
        new_session
    )

    response_data = super_admin.api.user_api.create_user(new_data)
    update_user_data = {"roles": ["USER", "ADMIN"]}
    super_admin.api.user_api.update_user(response_data.json()['id'], update_user_data, expected_status=200)
    admin_user.api.auth_api.authenticate_user(admin_user.creds)

    yield admin_user

    user_id = response_data.json()['id']
    if user_id is not None:
        super_admin.api.user_api.delete_user(user_id, expected_status=200)