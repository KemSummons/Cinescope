from clients.api_manager import ApiManager


class TestMovieAPI:
    """
    Позитивные тесты для хендлера movie
    """
    # в будущем почти все ассерты будут заменены с помощью pydantic

    @staticmethod
    def _assert_movie_structure(movie: dict) -> None:
        """Проверка структуры и типов полей объекта фильма."""
        assert "id" in movie, 'наличие "id" обязательно'
        assert isinstance(movie["id"], int), '"id" должно быть целым числом'
        assert movie["id"] > 0, '"id" должно быть больше 0'
        assert "name" in movie, 'наличие "name" обязательно'
        assert isinstance(movie["name"], str), '"name" должно быть строкой'
        assert "price" in movie, 'наличие "price" обязательно'
        assert isinstance(movie["price"], int), '"price" должно быть целым числом'
        assert movie["price"] > 0, '"price" должно быть больше 0'
        assert "location" in movie, 'наличие "location" обязательно'
        assert movie["location"] in ("MSK", "SPB"), '"location" может быть только "MSK" или "SPB"'
        assert "published" in movie, 'наличие "published" обязательно'
        assert isinstance(movie["published"], bool), '"published" должно быть булевым'
        assert "genreId" in movie, 'наличие "genreId" обязательно'
        assert isinstance(movie["genreId"], int), '"genreId" должно быть целым числом'
        assert movie["genreId"] > 0, '"genreId" должно быть больше 0'
        assert "description" in movie, 'наличие "description" обязательно'
        assert isinstance(movie["description"], str), '"description" должно быть строкой'
        if movie.get("imageUrl") is not None:
            assert isinstance(movie["imageUrl"], str), '"imageUrl" должно быть строкой или null'
        if movie.get("reviews") is not None:
            assert isinstance(movie["reviews"], list), '"reviews" должно быть списком'

    def test_create_movie(self, create_new_movie, test_movie):
        """
        Создание нового фильма
        """
        create_response = create_new_movie

        for key, expected_value in test_movie.items():
            assert key in create_response, f'в ответе отсутствует поле "{key}"'
            assert create_response[key] == expected_value, (
                f'поле "{key}": ожидалось {expected_value!r}, получено {create_response[key]!r}'
            )
        self._assert_movie_structure(create_response)

    def test_get_movies(self, api_manager: ApiManager):
        """
        Получение всех доступных фильмов
        """
        get_movies_response = api_manager.movie_api.get_movies(
            params={"pageSize": 5, "page": 1},
            expected_status=200
        )
        get_movies_response_data = get_movies_response.json()
        assert "movies" in get_movies_response_data, '"movies" отсутствует в ответе'
        assert isinstance(get_movies_response_data["movies"], list), '"movies" должно быть списком'
        assert len(get_movies_response_data["movies"]) > 0, '"movies" должен быть не пустым'
        for movie in get_movies_response_data["movies"]:
            self._assert_movie_structure(movie)
        assert get_movies_response_data["pageSize"] == 5, '"pageSize" должен быть 5'
        assert get_movies_response_data["page"] == 1, '"page" должен быть 1'

    def test_get_movie(self, api_manager: ApiManager, create_new_movie):
        """
        Получение информации по конкретному фильму
        """
        get_movie_response = api_manager.movie_api.get_movie(create_new_movie["id"], expected_status=200)
        get_movie_response_data = get_movie_response.json()

        for key, expected_value in create_new_movie.items():
            assert key in get_movie_response_data, f'в ответе отсутствует поле "{key}"'
            assert get_movie_response_data[key] == expected_value, (
                f'поле "{key}": ожидалось {expected_value!r}, получено {get_movie_response_data[key]!r}'
            )
        self._assert_movie_structure(get_movie_response_data)

    def test_update_movie(self, api_manager: ApiManager, create_new_movie, update_movie_data):
        """
        Обновление информации о фильме
        """
        movie_id = create_new_movie["id"]
        update_response = api_manager.movie_api.update_movie(
            movie_id=movie_id,
            movie_data=update_movie_data,
            expected_status=200
        )
        update_response_data = update_response.json()

        assert update_response_data["id"] == movie_id, '"id" фильма не совпадает'
        assert update_response_data["name"] == update_movie_data["name"], '"name" не обновилось'
        assert update_response_data["price"] == update_movie_data["price"], '"price" не обновилось'
        assert update_response_data["genreId"] == update_movie_data["genreId"], '"genreId" не обновилось'
        assert update_response_data["description"] == create_new_movie["description"], ('"description" не должно '
                                                                                        'обновляться')
        assert update_response_data["imageUrl"] == create_new_movie["imageUrl"], '"imageUrl" не должно обновляться'
        assert update_response_data["location"] == create_new_movie["location"], '"location" не должно обновляться'
        assert update_response_data["published"] == create_new_movie["published"], '"published" не должно обновляться'
        assert update_response_data["rating"] == create_new_movie["rating"], '"rating" не должно обновляться'
        assert update_response_data["createdAt"] == create_new_movie["createdAt"], '"createdAt" не должно обновляться'

    def test_delete_movie(self, api_manager: ApiManager, create_new_movie):
        """
        Удаление фильма
        """
        movie_id = create_new_movie["id"]
        delete_response = api_manager.movie_api.delete_movie(movie_id=movie_id, expected_status=200)
        deleted_movie_response = api_manager.movie_api.get_movie(movie_id=movie_id, expected_status=404)


class TestNegativeMovieAPI:
    """
    Негативные тесты для хендлера movie
    """
    def test_invalid_rules_creation(self, api_manager: ApiManager, test_movie):
        """
        Создание фильма без админских прав
        """
        create_response = api_manager.movie_api.create_movie(test_movie, expected_status=401)
        create_response_data = create_response.json()
        assert "message" in create_response_data, "в ответе об ошибке должно быть поле message"

    def test_invalid_body_creation(self, api_manager: ApiManager, super_admin_data):
        """
        Создание фильма без тела
        """
        api_manager.auth_api.authenticate_user(super_admin_data)
        create_response = api_manager.movie_api.create_movie(movie_data=None, expected_status=400)
        create_response_data = create_response.json()
        assert "message" in create_response_data, "в ответе об ошибке должно быть поле message"

    def test_non_full_body_creation(self, api_manager: ApiManager, super_admin_data):
        """
        Создание фильма с неполным телом
        """
        api_manager.auth_api.authenticate_user(super_admin_data)
        create_response = api_manager.movie_api.create_movie(movie_data={"name": "error name"}, expected_status=400)
        create_response_data = create_response.json()
        assert "message" in create_response_data, "в ответе об ошибке должно быть поле message"

    def test_negative_pagesize_limit(self, api_manager: ApiManager):
        """
        Превышение лимита pageSize (максимум 20)
        """
        get_movies_response = api_manager.movie_api.get_movies(
            params={"pageSize": 21},
            expected_status=400
        )
        get_movies_response_data = get_movies_response.json()
        assert "message" in get_movies_response_data, "в ответе об ошибке должно быть поле message"

    def test_negative_page_limit(self, api_manager: ApiManager):
        """
        Получение списка фильмов по page: -1
        """
        get_movies_response = api_manager.movie_api.get_movies(
            params={"page": -1},
            expected_status=400
        )
        get_movies_response_data = get_movies_response.json()
        assert "message" in get_movies_response_data, "в ответе об ошибке должно быть поле message"

    def test_get_non_existent_movie(self, api_manager: ApiManager):
        """
        Получение информации по несуществующему фильму
        """
        movie_response = api_manager.movie_api.get_movie(movie_id=999999999, expected_status=404)
        movie_response_data = movie_response.json()
        assert "message" in movie_response_data, "в ответе об ошибке должно быть поле message"

    def test_update_movie_without_rules(self, api_manager: ApiManager, update_movie_data):
        """
        Обновление информации о фильме без админских прав
        """
        update_response = api_manager.movie_api.update_movie(
            movie_id=999999999,
            movie_data=update_movie_data,
            expected_status=401
        )
        update_response_data = update_response.json()
        assert "message" in update_response_data, "в ответе об ошибке должно быть поле message"

    def test_update_non_existent_movie(self, api_manager: ApiManager, update_movie_data, super_admin_data):
        """
        Обновление информации о несуществующем фильме
        """
        api_manager.auth_api.authenticate_user(super_admin_data)
        update_response = api_manager.movie_api.update_movie(
            movie_id=999999999,
            movie_data=update_movie_data,
            expected_status=404
        )
        update_response_data = update_response.json()
        assert "message" in update_response_data, "в ответе об ошибке должно быть поле message"

    def test_delete_movie_without_rules(self, api_manager: ApiManager):
        """
        Удаление фильма без админских прав
        """
        delete_response = api_manager.movie_api.delete_movie(movie_id=1234, expected_status=401)
        delete_response_data = delete_response.json()
        assert "message" in delete_response_data, "в ответе об ошибке должно быть поле message"

    def test_delete_non_existent_movie(self, api_manager: ApiManager, super_admin_data):
        """
        Удаление несуществующего фильма
        """
        api_manager.auth_api.authenticate_user(super_admin_data)
        delete_response = api_manager.movie_api.delete_movie(movie_id=999999999, expected_status=404)
        delete_response_data = delete_response.json()
        assert "message" in delete_response_data, "в ответе об ошибке должно быть поле message"
