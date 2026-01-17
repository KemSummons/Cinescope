import requests
from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT, DELETE_USER_ENDPOINT
import pytest
from utils.data_generator import DataGenerator



@pytest.fixture(scope="session")
def test_user():
    """
    Генерация случайного пользователя для тестов.
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


@pytest.fixture(scope="session")
def auth_session(test_user):
    # Регистрируем нового пользователя
    register_url = f"{BASE_URL}{REGISTER_ENDPOINT}"
    response = requests.post(register_url, json=test_user, headers=HEADERS)
    assert response.status_code == 201, "Ошибка регистрации пользователя"

    # Логинимся для получения токена
    login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    response = requests.post(login_url, json=login_data, headers=HEADERS)
    assert response.status_code == 200, "Ошибка авторизации"

    # Получаем токен и создаём сессию
    token = response.json().get("accessToken")
    assert token is not None, "Токен доступа отсутствует в ответе"

    session = requests.Session()
    session.headers.update(HEADERS)
    session.headers.update({"Authorization": f"Bearer {token}"})
    return session

@pytest.fixture(scope="function")
def register_user():
    # на каждый тест генерируем нового пользователя
    password = DataGenerator.generate_random_password()
    user_data = {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": password,
        "passwordRepeat": password,
        "roles": ["USER"],
    }
    # Регистрируем нового пользователя
    register_url = f"{BASE_URL}{REGISTER_ENDPOINT}"
    response = requests.post(register_url, json=user_data, headers=HEADERS)
    print("REGISTER status:", response.status_code, "body:", response.text)
    assert response.status_code == 201, "Ошибка регистрации пользователя"
    user_id = response.json()["id"]

    # Получаем токен для удаления пользователя
    login_response = requests.post(
        f"{BASE_URL}{LOGIN_ENDPOINT}",
        json={"email": user_data["email"], "password": user_data["password"]},
        headers=HEADERS
    )
    assert login_response.status_code in [200, 201]
    token = login_response.json()["accessToken"]

    # Передаем данные для теста на авторизацию
    yield {"email": user_data["email"], "password": user_data["password"]}

    # Удаляем созданного пользователя и чистим бд
    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    delete_response = requests.delete(url=f"{BASE_URL}{DELETE_USER_ENDPOINT}{user_id}", headers=auth_headers)
    print(f"Cleanup DELETE {user_id}: status={delete_response.status_code}")
    if delete_response.status_code not in [200, 204, 202]:
        print(f"⚠️ Cleanup skipped: {delete_response.text}")
