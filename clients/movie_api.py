from constants import GET_OR_POST_MOVIES, GET_OR_DELETE_OR_PATCH_MOVIES
from custom_requester.custom_requester import CustomRequester


class MovieAPI(CustomRequester):
    """
    Класс для работы с API фильмов.
    """

    def __init__(self, session):
        super().__init__(session=session, base_url="https://api.dev-cinescope.coconutqa.ru")

    def get_movies(self, params=None, expected_status=200):
        """
        Получение информации о фильмах
        :param params: Query-параметры (например, {"limit": 5, "page": 1}).
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="GET",
            endpoint=GET_OR_POST_MOVIES,
            params=params,
            expected_status=expected_status,
            need_logging=True
        )

    def get_movie(self, movie_id, expected_status=200):
        """
        Получение информации о конкретном фильме
        :param movie_id: id конкретного фильма
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="GET",
            endpoint=GET_OR_DELETE_OR_PATCH_MOVIES.format(id=movie_id),
            expected_status=expected_status,
            need_logging=True
        )

    def create_movie(self, movie_data, expected_status=201):
        """
        Создание нового фильма
        :param movie_data: Данные для нового фильма
        :param expected_status: Ожидаемый статус-код
        """
        return self.send_request(
            method="POST",
            endpoint=GET_OR_POST_MOVIES,
            data=movie_data,
            expected_status=expected_status,
            need_logging=True
        )

    def delete_movie(self, movie_id, expected_status=200):
        """
        Удаление фильма
        :param movie_id: id конкретного фильма
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="DELETE",
            endpoint=GET_OR_DELETE_OR_PATCH_MOVIES.format(id=movie_id),
            expected_status=expected_status,
            need_logging=True
        )

    def update_movie(self, movie_id, movie_data, expected_status=200):
        """
        Частичное обновление информации о фильме
        :param movie_id: id конкретного фильма
        :param movie_data: данные для обновления фильма
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="PATCH",
            endpoint=GET_OR_DELETE_OR_PATCH_MOVIES.format(id=movie_id),
            data=movie_data,
            expected_status=expected_status,
            need_logging=True
        )
