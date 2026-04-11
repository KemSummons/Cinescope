from enum import Enum

BASE_URL = "https://auth.dev-cinescope.coconutqa.ru"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

LOGIN_ENDPOINT = "/login"
REGISTER_ENDPOINT = "/register"
DELETE_USER_ENDPOINT = "/user/"
LOGOUT_USER = "/logout/"
GET_OR_POST_MOVIES = "/movies"
GET_OR_DELETE_OR_PATCH_MOVIES = "/movies/{id}"

class Roles(Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"

ROLE_HIERARCHY = {
    Roles.USER: [Roles.USER.value],
    Roles.ADMIN: [Roles.USER.value, Roles.ADMIN.value],
    Roles.SUPER_ADMIN: [Roles.USER.value, Roles.ADMIN.value, Roles.SUPER_ADMIN.value],
}

def get_roles(role: Roles) -> list[str]:
    """
    Возвращает список ролей для данного уровня доступа.
    USER      → ["USER"]
    ADMIN     → ["USER", "ADMIN"]
    SUPER_ADMIN → ["USER", "ADMIN", "SUPER_ADMIN"]
    """
    return ROLE_HIERARCHY[role]