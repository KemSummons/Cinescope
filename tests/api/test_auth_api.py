from clients.api_manager import ApiManager


class TestAuthAPI:
    def test_register_user(self, api_manager: ApiManager, test_user):
        """
        Тест на регистрацию пользователя.
        """
        response = api_manager.auth_api.register_user(test_user)
        response_data = response.json()

        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

    def test_register_and_login_user(self, api_manager: ApiManager, registered_user):
        """
        Тест на регистрацию и авторизацию пользователя.
        """
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()

        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
        assert response_data["user"]["email"] == registered_user["email"], "Email не совпадает"

    def test_logout_user(self, api_manager: ApiManager, registered_user):
        """
        Тест на логаут пользователя.
        """
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()
        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
        assert response_data["user"]["email"] == registered_user["email"], "Email не совпадает"

        headers = {"Authorization": f"Bearer {response_data['accessToken']}"}
        api_manager.auth_api._update_session_headers(**headers)

        logout_response = api_manager.auth_api.logout_user()
        logout_response_data = logout_response.text.strip()
        assert logout_response_data == "OK", f"Expected 'OK', got '{logout_response_data}'"

class TestNegativeAuthAPI:
    def test_login_nonexistent_email(self, api_manager: ApiManager):
        """401 при логине несуществующего email"""

        login_data = {"email": "nonexistent@gmail.com", "password": "any"}
        login_response = api_manager.auth_api.login_user(login_data, expected_status=401)

        assert "accessToken" not in login_response.json()

    def test_login_invalid_email_format(self, api_manager: ApiManager):
        """401 при невалидном формате email"""
        login_data = {"email": "nonexistentgmail.com", "password": "any"}
        login_response = api_manager.auth_api.login_user(login_data, expected_status=401)
        assert "accessToken" not in login_response.json()

    def test_login_wrong_password(self, api_manager: ApiManager, registered_user):
        """Неправильный пароль для существующего пользователя"""
        login_data = {
            "email": registered_user["email"],
            "password": "wrong pass"
        }
        response = api_manager.auth_api.login_user(login_data, expected_status=401)
        response_data = response.json()
        assert "accessToken" not in response_data, "accessToken не должен быть при неверном пароле"
        assert "неверный" in response_data["message"].lower()

    def test_login_missing_body(self, api_manager: ApiManager):
        """Отправка запроса с пустым телом"""
        response = api_manager.auth_api.login_user(login_data=None, expected_status=401)
        response_data = response.json()
        assert "accessToken" not in response_data, "accessToken не должен быть"
        assert "неверный" in response_data.get("message", "").lower(), "Сообщение об ошибке"