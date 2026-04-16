from constants import Roles


class TestUserApi:
    """
    Позитивные тесты для хендлера user
    """

    def test_create_user(self, super_admin, user_factory):
        user_data = user_factory()
        user_response = super_admin.api.user_api.create_user(user_data).json()

        assert user_response['id'] is not None, "ID не должен быть None"
        assert user_response['id'] != '', "ID не должен быть пустой строкой"
        assert len(user_response['id']) > 0, "ID должен иметь длину"
        assert user_response.get('email') == user_data['email']
        assert user_response.get('fullName') == user_data['fullName']
        assert user_response.get('roles') == user_data['roles']
        assert user_response.get('verified') is True

    def test_get_user_by_locator(self, super_admin, user_factory):
        user_data = user_factory()
        user_response = super_admin.api.user_api.create_user(user_data).json()
        response_by_id = super_admin.api.user_api.get_user_info(user_response['id']).json()
        response_by_email = super_admin.api.user_api.get_user_info(user_response['email']).json()

        assert response_by_id == response_by_email, "Содержание ответов должно быть идентичным"
        assert response_by_id.get('id') and response_by_id['id'] != '', "ID должен быть не пустым"
        assert response_by_id.get('email') == user_data['email']
        assert response_by_id.get('fullName') == user_data['fullName']
        assert response_by_id.get('roles') == user_data['roles']
        assert response_by_id.get('verified') is True
