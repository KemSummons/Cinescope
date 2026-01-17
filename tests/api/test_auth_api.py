import pytest
import requests
from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT


class TestAuthAPI:
    def test_register_user(self, test_user):
        """Корректная регистрация"""
        register_url = f"{BASE_URL}{REGISTER_ENDPOINT}"

        response = requests.post(register_url, json=test_user, headers=HEADERS)

        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        assert response.status_code == 201, "Ошибка регистрации пользователя"
        response_data = response.json()
        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"

        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

    def test_login_user(self, register_user):
        """Корректная авторизация"""
        login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"

        response = requests.post(
            url=login_url,
            json={"email": register_user["email"], "password": register_user["password"]},
            headers=HEADERS
        )

        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        assert response.status_code in [200, 201]
        token = response.json()["accessToken"]
        assert token is not None

class TestNegativeAuthAPI:
    def test_login_nonexistent_email(self):
        """Логин несуществующего пользователя."""
        login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"

        response = requests.post(
            url=login_url,
            json={"email": "nonexistent@gmail.com", "password": "any"},
            headers=HEADERS
        )

        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        assert response.status_code == 401, "Несуществующий email"
        assert "accessToken" not in response.json()

    def test_login_invalid_email_format(self):
        """Невалидный формат email."""
        login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"
        response = requests.post(
            f"{login_url}",
            json={"email": "invalid-email", "password": "pass"},
            headers=HEADERS
        )

        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        assert response.status_code == 401

    def test_login_wrong_password(self, register_user):
        """Неправильный пароль для существующего пользователя."""
        login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"

        response = requests.post(
            url=login_url,
            json={"email": register_user["email"], "password": "wrong_password"},
            headers=HEADERS
        )

        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        assert response.status_code == 401
        assert "accessToken" not in response.json()

    def test_login_missing_body(self):
        """Отсутствует body запроса."""
        login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"
        response = requests.post(url=login_url, headers=HEADERS)

        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        assert response.status_code == 401
