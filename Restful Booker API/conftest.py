import pytest
import requests
from faker import Faker
from constants import HEADERS, BASE_URL


faker = Faker()

@pytest.fixture(scope="session")
def auth_session():
    session = requests.Session()
    session.headers.update(HEADERS)

    response = requests.post(
        f"{BASE_URL}/auth",
        headers=HEADERS,
        json={"username": "admin", "password": "password123"}
    )
    assert response.status_code == 200, "Ошибка авторизации"
    token = response.json().get("token")
    assert token is not None, "В ответе не оказалось токена"

    session.headers.update({"Cookie": f"token={token}"})
    return session

@pytest.fixture
def invalid_auth_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    session.headers.update({"Cookie": "token=invalid"})
    return session

@pytest.fixture
def booking_data():
    return {
        "firstname": faker.first_name(),
        "lastname": faker.last_name(),
        "totalprice": faker.random_int(min=100, max=100000),
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2024-04-05",
            "checkout": "2024-04-08"
        },
        "additionalneeds": "Cigars"
    }

@pytest.fixture
def invalid_booking_data_types():
    return {
        "firstname": 123,
        "lastname": 123,
        "totalprice": 'ten',
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2024-04-05",
            "checkout": "2024-04-08"
        },
        "additionalneeds": "Cigars"
    }

@pytest.fixture
def invalid_booking_data_fields():
    return {
        "firstname": faker.first_name(),
        "totalprice": faker.random_int(min=100, max=100000),
        "depositpaid": True,
        "bookingdates": {},
        "additionalneeds": "Cigars"
    }

@pytest.fixture(scope='function')
def created_booking(auth_session, booking_data):
    response = auth_session.post(f"{BASE_URL}/booking", json=booking_data)
    assert response.status_code == 200
    return response.json()

@pytest.fixture
def update_booking_data():
    return {
        "firstname": faker.first_name(),
        "lastname": faker.last_name(),
        "totalprice": faker.random_int(min=100, max=100000),
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2024-04-10",
            "checkout": "2024-04-20"
        },
        "additionalneeds": "Wine"
    }

@pytest.fixture
def partial_update_booking_data():
    return {
        "firstname": faker.first_name(),
        "lastname": faker.last_name(),
    }