import pytest
import requests
from faker import Faker
from datetime import timedelta
from RestfulBookerAPI.constants import BASE_URL, CREATE_BOOKING_ENDPOINT, CREATE_TOKEN_ENDPOINT, GET_BOOKING_ID_ENDPOINT
from RestfulBookerAPI.booker_custom_requester import BookerCustomRequester


@pytest.fixture(scope="session")
def faker() -> Faker:
    return Faker()


@pytest.fixture(scope="session")
def booking_data(faker):
    """
    Генерация случайного пользователя для тестов.
    """
    checkin = faker.date_between(start_date='-1y', end_date='today')
    checkout = checkin + timedelta(days=faker.random_int(min=1, max=30))

    return {
        "firstname": faker.first_name(),
        "lastname": faker.last_name(),
        "totalprice": faker.random_int(min=100, max=10000),  # Реалистичные цены
        "depositpaid": faker.boolean(chance_of_getting_true=70),  # 70% True
        "bookingdates": {
            "checkin": checkin.strftime("%Y-%m-%d"),
            "checkout": checkout.strftime("%Y-%m-%d")
        },
        "additionalneeds": faker.sentence(nb_words=2, variable_nb_words=True)  # "Breakfast required"
    }


@pytest.fixture(scope="function")
def invalid_data(faker):
    return {
        "firstname": 123,
        "lastname": faker.last_name(),
        "totalprice": faker.random_int(min=100, max=10000),  # Реалистичные цены
        "depositpaid": 'yes',  # 70% True
        "bookingdates": {
            "checkin": 'today',
            "checkout": 'not today'
        },
        "additionalneeds": faker.sentence(nb_words=2, variable_nb_words=True)  # "Breakfast required"
    }


@pytest.fixture(scope="function")
def update_data(faker):
    checkin = faker.date_between(start_date='-1y', end_date='today')
    checkout = checkin + timedelta(days=faker.random_int(min=1, max=30))

    return {
        "firstname": faker.first_name(),
        "lastname": faker.last_name(),
        "totalprice": faker.random_int(min=100, max=10000),  # Реалистичные цены
        "depositpaid": faker.boolean(chance_of_getting_true=70),  # 70% True
        "bookingdates": {
            "checkin": checkin.strftime("%Y-%m-%d"),
            "checkout": checkout.strftime("%Y-%m-%d")
        },
        "additionalneeds": faker.sentence(nb_words=2, variable_nb_words=True)  # "Breakfast required"
    }


@pytest.fixture(scope='function')
def created_booking(requester, booking_data):
    """Создаёт бронирование и возвращает response.json()."""
    response = requester.send_request(
        method='POST',
        endpoint=CREATE_BOOKING_ENDPOINT,
        data=booking_data,
        expected_status=200
    )
    return response.json()


@pytest.fixture(scope='function')
def get_token(requester):
    """Получение токена"""
    login_data = {"username" : "admin", "password" : "password123"}
    response = requester.send_request(
        method="POST",
        endpoint=CREATE_TOKEN_ENDPOINT,
        data=login_data,
        expected_status=200,
        need_logging=True
    )
    return response.json()["token"]


@pytest.fixture(scope="session")
def requester():
    """
    Фикстура для создания экземпляра CustomRequester.
    """
    session = requests.Session()
    return BookerCustomRequester(session=session, base_url=BASE_URL)