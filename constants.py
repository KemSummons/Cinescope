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