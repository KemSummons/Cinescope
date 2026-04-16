from clients.api_manager import ApiManager


class TestAuthAPI:
    def test_register_user(self, authenticated_admin, user_factory):
        """
        Тест на регистрацию пользователя.
        """
        user_data = user_factory()
        new_user = authenticated_admin.user_api.create_user(user_data)
        new_user_data = new_user.json()

        assert new_user_data["email"] == user_data["email"], "Email должны совпадать"
        assert "id" in new_user_data, "ID пользователя отсутствует в ответе"
        assert "roles" in new_user_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in new_user_data["roles"], "У пользователя должна быть роль USER"

    def test_register_and_login_user(self, api_manager: ApiManager, registered_and_logged_user):
        """
        Тест на регистрацию и авторизацию пользователя.
        """
        user_data = registered_and_logged_user
        user = user_data["user"]
        access_token = user_data["accessToken"]

        assert access_token, "accessToken должен быть непустой строкой"
        assert isinstance(access_token, str), "accessToken должен быть строкой"
        assert isinstance(user, dict), "Поле user отсутствует или имеет неверный формат"
        assert isinstance(user.get("id"), str), "id пользователя должен быть строкой"
        assert user.get("id"), "id пользователя должен быть непустой строкой"
        assert isinstance(user.get("email"), str), "email пользователя должен быть строкой"
        assert user.get("email"), "email пользователя должен быть непустой строкой"
        assert isinstance(user.get("roles"), list), "roles должен быть списком"
        assert "USER" in user["roles"], "У пользователя должна быть роль USER"

    def test_logout_user(self, authenticated_admin):
        """
        Тест на логаут пользователя.
        """
        logout_response = authenticated_admin.auth_api.logout_user()
        logout_response_data = logout_response.text.strip()
        assert logout_response_data == "OK", f"Expected 'OK', got '{logout_response_data}'"
        authenticated_admin.user_api.get_users(expected_status=401)

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