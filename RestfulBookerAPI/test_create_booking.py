import pytest
from faker import Faker

from RestfulBookerAPI.constants import (
    CREATE_BOOKING_ENDPOINT,
    UPDATE_BOOKING_ENDPOINT,
    PARTIAL_UPDATE_BOOKING_ENDPOINT,
    DELETE_BOOKING_ENDPOINT,
)
from RestfulBookerAPI.helpers import get_booking

class TestBookings:
    def test_create_booking(self, created_booking, booking_data):
        """Создание бронирования"""
        booking_id = created_booking["bookingid"]
        assert booking_id > 0, "bookingid должен быть положительным"

        booking = created_booking["booking"]
        assert booking == booking_data, "Данные бронирования не совпадают с отправленными"

    def test_get_booking(self, created_booking, requester):
        """Получение бронирования по ID"""
        get_booking_data = get_booking(requester, created_booking["bookingid"])
        assert get_booking_data == created_booking["booking"], "Полученное бронирование не совпадает с созданным"

    def test_update_booking(self, created_booking, requester, update_data, get_token):
        """Полное обновление бронирования"""
        booking_id = created_booking["bookingid"]
        assert booking_id > 0, "bookingid должен быть положительным"

        # Проверяем, что бронирование можно получить по ID
        get_booking_data = get_booking(requester, booking_id)
        assert get_booking_data == created_booking["booking"], "Полученное бронирование не совпадает с созданным"

        # Обновляем бронирование (токен передаётся в Cookie)
        update_response = requester.send_request(
            method='PUT',
            endpoint=UPDATE_BOOKING_ENDPOINT.format(id=booking_id),
            data=update_data,
            expected_status=200,
            need_logging=True,
            headers={"Cookie": f"token={get_token}"}
        )

        # Проверяем, что данные бронирования обновились
        get_booking_data = get_booking(requester, booking_id)
        assert get_booking_data == update_data, "Полученное бронирование не обновилось"

    def test_partial_update_booking(self, created_booking, requester, get_token, faker):
        """Частичное обновление бронирования"""
        booking_id = created_booking["bookingid"]
        assert booking_id > 0, "bookingid должен быть положительным"

        # Проверяем, что бронирование можно получить по ID
        get_booking_data = get_booking(requester, booking_id)
        assert get_booking_data == created_booking["booking"], "Полученное бронирование не совпадает с созданным"

        # Обновляем бронирование
        new_data = {
            "firstname": faker.first_name(),
            "additionalneeds": faker.sentence(nb_words=2, variable_nb_words=True),
        }

        update_response = requester.send_request(
            method='PATCH',
            endpoint=PARTIAL_UPDATE_BOOKING_ENDPOINT.format(id=booking_id),
            data=new_data,
            expected_status=200,
            need_logging=True,
            headers={"Cookie": f"token={get_token}"}
        )
        update_response_data = update_response.json()
        assert update_response_data["firstname"] == new_data["firstname"], "firstname должно совпадать"
        assert update_response_data["additionalneeds"] == new_data["additionalneeds"], ("additionalneeds должно "
                                                                                        "совпадать")

        # Проверяем, что данные бронирования обновились
        get_booking_data = get_booking(requester, booking_id)
        assert get_booking_data["firstname"] == new_data["firstname"], "firstname должно совпадать"
        assert get_booking_data["additionalneeds"] == new_data["additionalneeds"], "additionalneeds должно совпадать"

    def test_delete_booking(self, requester, created_booking, get_token):
        """Удаление бронирования"""
        booking_id = created_booking["bookingid"]
        assert booking_id > 0, "bookingid должен быть положительным"

        # Проверяем, что бронирование можно получить по ID
        get_booking_data = get_booking(requester, booking_id)
        assert get_booking_data == created_booking["booking"], "Полученное бронирование не совпадает с созданным"

        # Удаляем бронирование
        delete_response = requester.send_request(
            method='DELETE',
            endpoint=DELETE_BOOKING_ENDPOINT.format(id=booking_id),
            expected_status=201,
            need_logging=True,
            headers={"Cookie": f"token={get_token}"}
        )

        # Проверяем, что бронирование больше недоступно
        get_booking(requester, booking_id, expected_status=404)


class TestNegativeBookings:
    def test_negative_types_create_booking(self, requester, invalid_data):
        """Создание с некорректными типами данных"""
        negative_create = requester.send_request(
            method="POST",
            endpoint=CREATE_BOOKING_ENDPOINT,
            data=invalid_data,
            expected_status=500,
            need_logging=True
        )

    def test_negative_fields_create_booking(self, requester):
        """Создание с некорректным телом"""
        user_data = {"firstname": 'Van', "lastname": "Darkholm"}
        negative_create = requester.send_request(
            method="POST",
            endpoint=CREATE_BOOKING_ENDPOINT,
            data=user_data,
            expected_status=500,
            need_logging=True
        )

    def test_negative_update_non_existent_booking(self, requester, update_data, get_token):
        """Обновление несуществующего бронирования"""
        update_response = requester.send_request(
            method="PUT",
            endpoint=UPDATE_BOOKING_ENDPOINT.format(id=999999999),
            data=update_data,
            expected_status=405,
            need_logging=True,
            headers={"Cookie": f"token={get_token}"}
        )

    def test_negative_delete_booking(self, created_booking, requester, get_token):
        """Удаление бронирования без токена"""
        booking_id = created_booking["bookingid"]
        assert booking_id > 0, "bookingid должен быть положительным"

        # Проверяем, что бронирование можно получить по ID
        get_booking_data = get_booking(requester, created_booking["bookingid"])
        assert get_booking_data == created_booking["booking"], "Полученное бронирование не совпадает с созданным"

        # Удаляем бронирование
        delete_response = requester.send_request(
            method='DELETE',
            endpoint=DELETE_BOOKING_ENDPOINT.format(id=booking_id),
            expected_status=403,
            need_logging=True
        )