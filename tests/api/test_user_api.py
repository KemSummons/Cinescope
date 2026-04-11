from constants import Roles


class TestUserApi:
    """
    Позитивные тесты для хендлера user
    """

    def test_create_user(self, super_admin, creation_user_factory):
        user_data = creation_user_factory(role=Roles.ADMIN)
        response = super_admin.api.user_api.create_user(user_data).json()
        print(response)
        print(user_data)
        assert response['id'] is not None, "ID не должен быть None"
        assert response['id'] != '', "ID не должен быть пустой строкой"
        assert len(response['id']) > 0, "ID должен иметь длину"
        assert response.get('email') == user_data['email']
        assert response.get('fullName') == user_data['fullName']
        # assert response.get('roles', []) == user_data['roles']
        assert response.get('verified') is True

        user_data_id = response["id"]
        print(user_data_id)
        update_user_data = {"roles": ["USER", "ADMIN"]}
        super_admin.api.user_api.update_user(user_data_id, update_user_data, expected_status=200)

    def test_get_user_by_locator(self, super_admin, creation_user_data):
        creation_user_response = super_admin.api.user_api.create_user(creation_user_data).json()
        response_by_id = super_admin.api.user_api.get_user_info(creation_user_response['id']).json()
        response_by_email = super_admin.api.user_api.get_user_info(creation_user_response['email']).json()

        assert response_by_id == response_by_email, "Содержание ответов должно быть идентичным"
        assert response_by_id.get('id') and response_by_id['id'] != '', "ID должен быть не пустым"
        assert response_by_id.get('email') == creation_user_data['email']
        assert response_by_id.get('fullName') == creation_user_data['fullName']
        assert response_by_id.get('roles', []) == creation_user_data['roles']
        assert response_by_id.get('verified') is True
