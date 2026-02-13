from constants import REGISTER_ENDPOINT, LOGIN_ENDPOINT, LOGOUT_USER
from custom_requester.custom_requester import CustomRequester


class AuthAPI(CustomRequester):
    """Класс для работы с аутентификацией"""
    def __init__(self, session):
        super().__init__(session=session, base_url="https://auth.dev-cinescope.coconutqa.ru")

    def register_user(self, user_data, expected_status=201):
        """
        Регистрация нового пользователя.
        :param user_data: Данные пользователя.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=user_data,
            expected_status=expected_status
        )

    def login_user(self, login_data, expected_status=200):
        """
        Авторизация пользователя.
        :param login_data: Данные для логина.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=expected_status
        )

    def authenticate_user(self, user_creds):
        login_data = {
            "email": user_creds["username"],
            "password": user_creds["password"]
        }
        response = self.login_user(login_data).json()
        if "accessToken" not in response:
            raise KeyError("token is missing")

        token = response["accessToken"]
        self._update_session_headers(**{"authorization": "Bearer " + token})

    def logout_user(self, expected_status=200):
        """
        Логаут пользователя.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="GET",
            endpoint=LOGOUT_USER,
            expected_status=expected_status,
            need_logging=True
        )
