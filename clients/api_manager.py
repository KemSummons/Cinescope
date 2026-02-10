from clients.auth_api import AuthAPI
from clients.user_api import UserAPI

class ApiManager:
    """
    Класс для управления API-классами с единой HTTP-сессией.
    """
    def __init__(self, session, base_url):
        """
        Инициализация ApiManager.
        :param session: HTTP-сессия, используемая всеми API-классами.
        :param base_url: Базовый URL API (для UserAPI и др.).
        """
        self.session = session
        self.base_url = base_url
        self.auth_api = AuthAPI(session)
        self.user_api = UserAPI(session, base_url)
