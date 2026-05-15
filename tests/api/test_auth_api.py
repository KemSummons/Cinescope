import allure
import pytest
from clients.api_manager import ApiManager
from models.auth_api_models import RegisterUserResponse, LoginUserResponse


@pytest.mark.regression
class TestAuthAPI:
    @allure.title("Регистрация нового пользователя")
    @allure.description("Проверка создания нового пользователя и назначения ему роли USER")
    @pytest.mark.smoke
    def test_register_user(self, user_session, user_factory, created_users_cleanup):
        guest_api = user_session()
        user_data = user_factory()
        response = guest_api.auth_api.register_user(user_data)
        register_user_response = RegisterUserResponse(**response.json())
        assert register_user_response.email == user_data.email, "Email должны совпадать"
        assert "USER" in register_user_response.roles, "У пользователя должна быть роль USER"
        created_users_cleanup(register_user_response.id)

    @allure.title("Регистрация и вход пользователя")
    @allure.description("Проверка успешной регистрации и авторизации пользователя")
    @pytest.mark.smoke
    def test_register_and_login_user(self, registered_and_logged_user):
        login_user_response = LoginUserResponse(**registered_and_logged_user)
        assert "USER" in login_user_response.user.roles, "У пользователя должна быть роль USER"
        assert login_user_response.user.email is not None, "У пользователя должен быть корректный email"
        assert login_user_response.accessToken, "У пользователя должен быть accessToken"
        assert login_user_response.refreshToken, "У пользователя должен быть refreshToken"

    @allure.title("Выход пользователя из системы")
    @allure.description("Проверка логаута пользователя и последующего ограничения доступа к API")
    def test_logout_user(self, authenticated_admin):
        logout_response = authenticated_admin.auth_api.logout_user()
        assert logout_response.text.strip() == "OK", f"Expected 'OK', got '{logout_response.text}'"
        authenticated_admin.user_api.get_users(expected_status=401)


@pytest.mark.negative
class TestNegativeAuthAPI:
    @allure.title("Логин с несуществующим email")
    @allure.description("Проверка авторизации с несуществующим email")
    def test_login_nonexistent_email(self, api_manager: ApiManager):
        login_data = {"email": "nonexistent@gmail.com", "password": "any"}
        login_response = api_manager.auth_api.login_user(login_data, expected_status=401)
        assert "accessToken" not in login_response.json()

    @allure.title("Логин с невалидным форматом email")
    @allure.description("Проверка авторизации с невалидным email")
    def test_login_invalid_email_format(self, api_manager: ApiManager):
        login_data = {"email": "nonexistentgmail.com", "password": "any"}
        login_response = api_manager.auth_api.login_user(login_data, expected_status=401)
        assert "accessToken" not in login_response.json()

    @allure.title("Логин с неверным паролем")
    @allure.description("Проверка авторизации с некорректным паролем")
    def test_login_wrong_password(self, api_manager: ApiManager, registered_user):
        login_data = {
            "email": registered_user["email"],
            "password": "wrong pass"
        }
        response = api_manager.auth_api.login_user(login_data, expected_status=401)
        response_data = response.json()
        assert "accessToken" not in response_data, "accessToken не должен быть при неверном пароле"
        assert "неверный" in response_data["message"].lower()

    @allure.title("Логин с пустым телом запроса")
    @allure.description("Проверка авторизации с пустым телом запроса")
    def test_login_missing_body(self, api_manager: ApiManager):
        response = api_manager.auth_api.login_user(login_data=None, expected_status=401)
        response_data = response.json()
        assert "accessToken" not in response_data, "accessToken не должен быть"
        assert "неверный" in response_data.get("message", "").lower(), "Сообщение об ошибке"
