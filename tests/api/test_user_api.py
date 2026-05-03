import pytest
from constants import Roles
from helpers import assert_common_fields_equal
from models.user_api_models import CreateUserResponse, GetAllUsersResponse


class TestUserApi:
    """
    Позитивные тесты для хендлера user
    """

    def test_create_user(self, super_admin, user_factory, created_users_cleanup):
        user_data = user_factory()
        create_response = super_admin.api.user_api.create_user(user_data)
        create_response_data = CreateUserResponse(**create_response.json())
        created_users_cleanup(create_response_data.id)
        assert_common_fields_equal(user_data, create_response_data)

    def test_get_user_by_locator(self, super_admin, user_factory, created_users_cleanup):
        user_data = user_factory()
        create_response = super_admin.api.user_api.create_user(user_data)
        create_response_data = CreateUserResponse(**create_response.json())
        created_users_cleanup(create_response_data.id)
        response_by_id = super_admin.api.user_api.get_user_info(create_response_data.id)
        user_with_id_data = CreateUserResponse(**response_by_id.json())
        response_by_email = super_admin.api.user_api.get_user_info(create_response_data.email)
        user_with_email_data = CreateUserResponse(**response_by_email.json())
        assert_common_fields_equal(create_response_data, user_with_id_data)
        assert_common_fields_equal(create_response_data, user_with_email_data)

    def test_update_user(self, super_admin, user_factory, created_users_cleanup):
        user_data = user_factory()
        create_response = super_admin.api.user_api.create_user(user_data)
        create_response_data = CreateUserResponse(**create_response.json())
        created_users_cleanup(create_response_data.id)
        update_data = {"verified": False, "banned": True, "roles": ["USER", "ADMIN"]}
        super_admin.api.user_api.update_user(create_response_data.id, update_data)
        updated_user_response = super_admin.api.user_api.get_user_info(create_response_data.id)
        updated_user_data = CreateUserResponse(**updated_user_response.json())
        assert updated_user_data.verified == update_data["verified"]
        assert updated_user_data.banned == update_data["banned"]
        assert updated_user_data.roles == update_data["roles"]
        assert_common_fields_equal(
            create_response_data,
            updated_user_data,
            exclude_fields={"verified", "banned", "roles"},
        )

    def test_delete_user(self, super_admin, user_factory):
        user_data = user_factory()
        create_response = super_admin.api.user_api.create_user(user_data)
        create_response_data = CreateUserResponse(**create_response.json())
        super_admin.api.user_api.delete_user(create_response_data.id)
        get_response = super_admin.api.user_api.get_user_info(create_response_data.id)
        assert get_response.json() == {}

    def test_get_all_users(self, super_admin):
        response = super_admin.api.user_api.get_users(
            params={"pageSize": 5, "page": 3, "roles": ["ADMIN"], "createdAt": "desc"}
        )
        response_data = GetAllUsersResponse(**response.json())
        assert response_data.page == 3
        assert response_data.pageSize == 5
        assert len(response_data.users) <= 5
        assert response_data.count >= 0
        for user in response_data.users:
            assert Roles.ADMIN in user.roles


class TestNegativeUserApi:
    """
    Негативные тесты для хендлера user
    """

    def test_create_user_without_permissions(self, create_common_user, user_factory):
        user_data = user_factory()
        create_response = create_common_user.api.user_api.create_user(user_data, expected_status=403)
        create_response_data = create_response.json()
        assert "message" in create_response_data
        assert "Forbidden" == create_response_data["error"]

    def test_create_user_with_empty_body(self, super_admin):
        create_response = super_admin.api.user_api.create_user(user_data=None, expected_status=400)
        create_response_data = create_response.json()
        assert "message" in create_response_data
        assert "Bad Request" == create_response_data["error"]

    def test_create_user_with_duplicate_email(self, super_admin, user_factory, created_users_cleanup):
        user_data = user_factory()
        first_create_response = super_admin.api.user_api.create_user(user_data, expected_status=201)
        first_create_response_data = CreateUserResponse(**first_create_response.json())
        created_users_cleanup(first_create_response_data.id)
        duplicate_response = super_admin.api.user_api.create_user(user_data, expected_status=409)
        duplicate_response_data = duplicate_response.json()
        assert "message" in duplicate_response_data
        assert "Conflict" == duplicate_response_data["error"]

    def test_update_user_without_permissions(
            self, super_admin, create_common_user, user_factory, created_users_cleanup
    ):
        user_data = user_factory()
        create_response = super_admin.api.user_api.create_user(user_data)
        create_response_data = CreateUserResponse(**create_response.json())
        created_users_cleanup(create_response_data.id)
        update_response = create_common_user.api.user_api.update_user(
            create_response_data.id,
            {"verified": False},
            expected_status=403,
        )
        assert "message" in update_response.json()

    def test_update_deleted_user(self, super_admin, user_factory):
        user_data = user_factory()
        create_response = super_admin.api.user_api.create_user(user_data)
        create_response_data = CreateUserResponse(**create_response.json())
        super_admin.api.user_api.delete_user(create_response_data.id)
        update_response = super_admin.api.user_api.update_user(
            create_response_data.id,
            {"verified": False},
            expected_status=400,
        )
        assert "message" in update_response.json()

    def test_update_user_with_invalid_roles(self, super_admin, user_factory, created_users_cleanup):
        user_data = user_factory()
        create_response = super_admin.api.user_api.create_user(user_data)
        create_response_data = CreateUserResponse(**create_response.json())
        created_users_cleanup(create_response_data.id)
        update_response = super_admin.api.user_api.update_user(
            create_response_data.id,
            {"roles": ["INVALID_ROLE"]},
            expected_status=400,
        )
        assert "message" in update_response.json()
        assert "Bad Request" == update_response.json()["error"]

    def test_delete_user_without_permissions(
            self, super_admin, create_common_user, user_factory, created_users_cleanup
    ):
        user_data = user_factory()
        create_response = super_admin.api.user_api.create_user(user_data)
        create_response_data = CreateUserResponse(**create_response.json())
        created_users_cleanup(create_response_data.id)
        delete_response = create_common_user.api.user_api.delete_user(create_response_data.id, expected_status=403)
        assert "message" in delete_response.json()
        assert "Forbidden" == delete_response.json()["message"]

    def test_delete_user_with_invalid_id(self, super_admin):
        delete_response = super_admin.api.user_api.delete_user("invalid-id", expected_status=400)
        assert "message" in delete_response.json()
        assert "Bad Request" == delete_response.json()["error"]

    def test_delete_already_deleted_user(self, super_admin, user_factory):
        user_data = user_factory()
        create_response = super_admin.api.user_api.create_user(user_data)
        create_response_data = CreateUserResponse(**create_response.json())
        super_admin.api.user_api.delete_user(create_response_data.id, expected_status=200)
        second_delete_response = super_admin.api.user_api.delete_user(create_response_data.id, expected_status=404)
        assert "message" in second_delete_response.json()
        assert "Not Found" == second_delete_response.json()["message"]

    def test_get_non_existent_user_by_id(self, super_admin):
        get_response = super_admin.api.user_api.get_user_info(
            "00000000-0000-0000-0000-000000000000",
            expected_status=200
        )
        assert get_response.json() == {}

    def test_get_non_existent_user_by_email(self, super_admin):
        get_response = super_admin.api.user_api.get_user_info("user_not_found@qa.test", expected_status=200)
        assert get_response.json() == {}

    def test_get_user_info_unauthorized(self, user_session, super_admin, user_factory, created_users_cleanup):
        user_data = user_factory()
        create_response = super_admin.api.user_api.create_user(user_data)
        create_response_data = CreateUserResponse(**create_response.json())
        created_users_cleanup(create_response_data.id)
        guest_api = user_session()
        get_response = guest_api.user_api.get_user_info(create_response_data.id, expected_status=401)
        assert "message" in get_response.json()
        assert "Unauthorized" == get_response.json()["message"]

    def test_get_user_info_forbidden_for_user_role(
            self, create_common_user, super_admin, user_factory, created_users_cleanup
    ):
        user_data = user_factory()
        create_response = super_admin.api.user_api.create_user(user_data)
        create_response_data = CreateUserResponse(**create_response.json())
        created_users_cleanup(create_response_data.id)
        get_response = create_common_user.api.user_api.get_user_info(create_response_data.id, expected_status=403)
        assert "message" in get_response.json()
        assert "Forbidden" == get_response.json()["error"]

    def test_get_all_users_unauthorized(self, user_session):
        guest_api = user_session()
        get_response = guest_api.user_api.get_users(params={"page": 1, "pageSize": 3}, expected_status=401)
        assert "message" in get_response.json()
        assert "Unauthorized" == get_response.json()["message"]

    def test_get_all_users_forbidden_for_user_role(self, create_common_user):
        get_response = create_common_user.api.user_api.get_users(params={"page": 1, "pageSize": 3}, expected_status=403)
        assert "message" in get_response.json()
        assert "Forbidden" == get_response.json()["error"]

    def test_get_all_users_with_invalid_page(self, super_admin):
        get_response = super_admin.api.user_api.get_users(params={"page": -1, "pageSize": 5}, expected_status=400)
        assert "message" in get_response.json()
        assert "Bad Request" == get_response.json()["error"]

    @pytest.mark.parametrize(
        "params",
        [
            pytest.param({"page": -1, "pageSize": 5}, id="page-negative"),
            pytest.param({"page": 0, "pageSize": 5}, id="page-zero"),
            pytest.param({"page": 1, "pageSize": 0}, id="pageSize-zero"),
            pytest.param({"page": 1, "pageSize": -5}, id="pageSize-negative"),
        ],
    )
    def test_get_users_invalid_pagination(self, super_admin, params):
        response = super_admin.api.user_api.get_users(params=params, expected_status=400)
        assert "message" in response.json()
        assert response.json()["error"] == "Bad Request"
