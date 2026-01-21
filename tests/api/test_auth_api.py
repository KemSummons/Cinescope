import pytest
from constants import REGISTER_ENDPOINT, LOGIN_ENDPOINT, LOGOUT_USER


class TestAuthAPI:
    def test_register_user(self, requester, test_user):
        """
        Тест на регистрацию пользователя.
        """
        response = requester.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=test_user,
            expected_status=201
        )
        response_data = response.json()
        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

    def test_register_and_login_user(self, requester, registered_user):
        """
        Тест на регистрацию и авторизацию пользователя.
        """
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        response = requester.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=200
        )
        response_data = response.json()
        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
        assert response_data["user"]["email"] == registered_user["email"], "Email не совпадает"


    def test_logout_user(self, requester, registered_user):
        """
        Тест на логаут пользователя.
        """
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        response = requester.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=200
        )
        response_data = response.json()
        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
        assert response_data["user"]["email"] == registered_user["email"], "Email не совпадает"

        headers = {"Authorization": f"Bearer {response_data["accessToken"]}"}
        requester.headers.update(headers)

        logout_response = requester.send_request(
            method="GET",
            endpoint=LOGOUT_USER,
            expected_status=200
        )
        logout_response_data = logout_response.text.strip()
        assert logout_response_data == "OK", f"Expected 'OK', got '{logout_response_data}'"

class TestNegativeAuthAPI:
    def test_login_nonexistent_email(self, requester):
        """401 при логине несуществующего email"""

        login_data = {"email": "nonexistent@gmail.com", "password": "any"}
        login_response = requester.send_request(
            method='POST',
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=401
        )
        assert login_response.status_code == 401, "Несуществующий email"
        assert "accessToken" not in login_response.json()

    def test_login_invalid_email_format(self, requester):
        """401 при невалидном формате email"""
        login_data = {"email": "nonexistentgmail.com", "password": "any"}
        login_response = requester.send_request(
            method='POST',
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=401
        )
        assert login_response.status_code == 401, "Несуществующий email"
        assert "accessToken" not in login_response.json()

    def test_login_wrong_password(self, requester, registered_user):
        """Неправильный пароль для существующего пользователя"""
        login_data = {
            "email": registered_user["email"],
            "password": "wrong pass"
        }
        response = requester.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=401
        )
        response_data = response.json()
        assert "accessToken" not in response_data, "accessToken не должен быть при неверном пароле"
        assert response_data.get("statusCode") == 401
        assert "неверный" in response_data["message"].lower()

    def test_login_missing_body(self, requester):
        """Отправка запроса с пустым телом"""
        response = requester.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            expected_status=401
        )
        response_data = response.json()
        assert "accessToken" not in response_data, "accessToken не должен быть"
        assert response_data.get("statusCode") == 401, "Код ошибки в теле ответа"
        assert "неверный" in response_data.get("message", "").lower(), "Сообщение об ошибке"