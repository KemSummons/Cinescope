import pytest
import random
from clients.api_manager import ApiManager
from conftest import api_manager
from constants import Roles
from helpers import assert_common_fields_equal
from models.movie_api_models import GetAllMoviesResponse, CreateMovieResponse


class TestMovieAPI:
    """
    Позитивные тесты для хендлера movie
    """
    def test_create_movie(self, create_new_movie, movie_data):
        """
        Создание нового фильма
        """
        assert_common_fields_equal(create_new_movie, movie_data)

    def test_get_movies(self, api_manager: ApiManager):
        """
        Получение всех доступных фильмов
        """
        get_movies_response = api_manager.movie_api.get_movies(
            params={"pageSize": 5, "page": 1},
            expected_status=200
        )
        movies_response_data = GetAllMoviesResponse(**get_movies_response.json())
        assert movies_response_data.pageSize == 5, '"pageSize" должен быть 5'
        assert movies_response_data.page == 1, '"page" должен быть 1'

    @pytest.mark.slow
    def test_get_movie_for_common_user(self, create_new_movie, create_common_user):
        """
        Получение информации по конкретному фильму обычным пользователем
        """
        get_movie_response = create_common_user.api.movie_api.get_movie(create_new_movie.id, expected_status=200)
        movie_response = CreateMovieResponse(**get_movie_response.json())
        assert_common_fields_equal(create_new_movie, movie_response)

    def test_get_movie_for_unauthorized_user(self, create_new_movie_without_teardown, user_session, admin_delete_movie):
        """
        Получение информации по конкретному фильму неавторизованным пользователем
        """
        guest_api = user_session()
        get_movie_response = guest_api.movie_api.get_movie(create_new_movie_without_teardown.id, expected_status=200)
        movie_response = CreateMovieResponse(**get_movie_response.json())
        assert_common_fields_equal(create_new_movie_without_teardown, movie_response)
        admin_delete_movie(movie_id=create_new_movie_without_teardown.id)

    def test_update_movie(self, api_manager: ApiManager, create_new_movie, update_movie_data):
        """
        Обновление информации о фильме
        """
        update_response = api_manager.movie_api.update_movie(
            movie_id=create_new_movie.id,
            movie_data=update_movie_data,
            expected_status=200
        )
        update_response_data = CreateMovieResponse(**update_response.json())
        assert update_response_data.name == update_movie_data["name"]
        assert update_response_data.price == update_movie_data["price"]
        assert update_response_data.genreId == update_movie_data["genreId"]
        assert_common_fields_equal(
            create_new_movie,
            update_response_data,
            exclude_fields={"name", "price", "genreId", "genre"}
        )

    def test_delete_movie(self, api_manager: ApiManager, create_new_movie_without_teardown):
        """
        Удаление фильма
        """
        movie_id = create_new_movie_without_teardown.id
        api_manager.movie_api.delete_movie(movie_id=movie_id, expected_status=200)
        api_manager.movie_api.get_movie(movie_id=movie_id, expected_status=404)

    @pytest.mark.parametrize("min_price,max_price,locations,genre", [
        (random.randint(1, 500), random.randint(500, 1001), random.choice(['SPB', 'MSK']), random.randint(1, 10)),
        (random.randint(1, 100), random.randint(900, 1001), random.choice(['SPB', 'MSK']), random.randint(1, 10)),
        (1, 1000, random.choice(['SPB', 'MSK']), random.randint(1, 10))
    ],
        ids=['Test # 1', 'Test # 2', 'Test # 3']
    )
    def test_get_movies_with_parametrize(self, api_manager: ApiManager, min_price, max_price, locations, genre):
        params = {'minPrice': min_price, 'maxPrice': max_price, 'locations': locations, 'genreId': genre}
        response_movies = api_manager.movie_api.get_movies(params=params)
        movies_data = response_movies.json()

        assert movies_data['movies'], f"Фильмы не найдены для {params}"
        for i in range(len(movies_data['movies'])):
            assert movies_data['movies'][i]['genreId'] == genre
            assert movies_data['movies'][i]['location'] == locations
            assert min_price <= movies_data['movies'][i]['price'] <= max_price

    @pytest.mark.slow
    @pytest.mark.parametrize(
        'user_role', [Roles.USER, Roles.ADMIN, Roles.SUPER_ADMIN],
        ids=["Role: USER", "Role: ADMIN", "Role: SUPER_ADMIN"]
    )
    def test_delete_movie_all_roles(self, create_new_movie, create_user_with_any_role, user_role):
        user = create_user_with_any_role(role=user_role)
        movie_id = create_new_movie.id
        user.api.movie_api.delete_movie(
            movie_id=movie_id,
            expected_status=(200 if user_role == Roles.SUPER_ADMIN else 403)
        )

class TestNegativeMovieAPI:
    """
    Негативные тесты для хендлера movie
    """
    @pytest.mark.slow
    def test_invalid_rules_creation(self, create_common_user, movie_data):
        """
        Создание фильма без админских прав
        """
        create_response = create_common_user.api.movie_api.create_movie(movie_data, expected_status=403)
        create_response_data = create_response.json()
        assert "message" in create_response_data, "в ответе об ошибке должно быть поле message"

    def test_invalid_body_creation(self, authenticated_admin):
        """
        Создание фильма без тела
        """
        create_response = authenticated_admin.movie_api.create_movie(movie_data=None, expected_status=400)
        create_response_data = create_response.json()
        assert "message" in create_response_data, "в ответе об ошибке должно быть поле message"

    def test_non_full_body_creation(self, api_manager: ApiManager, authenticated_admin):
        """
        Создание фильма с неполным телом
        """
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

    @pytest.mark.slow
    def test_update_movie_without_rules(self, create_new_movie, create_common_user, update_movie_data):
        """
        Обновление информации о фильме без админских прав
        """
        update_response = create_common_user.api.movie_api.update_movie(
            movie_id=create_new_movie.id,
            movie_data=update_movie_data,
            expected_status=403
        )
        update_response_data = update_response.json()
        assert "message" in update_response_data, "в ответе об ошибке должно быть поле message"

    def test_update_non_existent_movie(self, authenticated_admin, update_movie_data):
        """
        Обновление информации о несуществующем фильме
        """
        update_response = authenticated_admin.movie_api.update_movie(
            movie_id=999999999,
            movie_data=update_movie_data,
            expected_status=404
        )
        update_response_data = update_response.json()
        assert "message" in update_response_data, "в ответе об ошибке должно быть поле message"

    @pytest.mark.slow
    def test_delete_movie_without_rules(self, create_new_movie, create_common_user):
        """
        Удаление фильма без админских прав
        """
        delete_response = create_common_user.api.movie_api.delete_movie(
            movie_id=create_new_movie.id,
            expected_status=403
        )
        delete_response_data = delete_response.json()
        assert "message" in delete_response_data, "в ответе об ошибке должно быть поле message"

    def test_delete_non_existent_movie(self, authenticated_admin):
        """
        Удаление несуществующего фильма
        """
        delete_response = authenticated_admin.movie_api.delete_movie(movie_id=999999999, expected_status=404)
        delete_response_data = delete_response.json()
        assert "message" in delete_response_data, "в ответе об ошибке должно быть поле message"
