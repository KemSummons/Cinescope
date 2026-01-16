import pytest
import requests

from constants import BASE_URL


class TestBookings:
    def test_create_booking(self, auth_session, created_booking, booking_data):
        # Создаём бронирование и проверяем его доступность
        booking_id = created_booking.get("bookingid")
        assert booking_id is not None, "Идентификатор брони не найден в ответе"
        assert created_booking["booking"]["firstname"] == booking_data["firstname"], "Заданное имя не совпадает"
        assert created_booking["booking"]["totalprice"] == booking_data["totalprice"], "Заданная стоимость не совпадает"

        # Проверяем, что бронирование можно получить по ID
        get_booking = auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        assert get_booking.status_code == 200, "Бронь не найдена"
        assert get_booking.json()["lastname"] == booking_data["lastname"], "Заданная фамилия не совпадает"

        # Удаляем бронирование
        deleted_booking = auth_session.delete(f"{BASE_URL}/booking/{booking_id}")
        assert deleted_booking.status_code == 201, "Бронь не удалилась"

        # Проверяем, что бронирование больше недоступно
        get_booking = auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        assert get_booking.status_code == 404, "Бронь не удалилась"

    def test_update_booking(self, auth_session, created_booking, booking_data, update_booking_data):
        # Создаём бронирование и проверяем его доступность
        booking_id = created_booking.get("bookingid")
        assert booking_id is not None, "Идентификатор брони не найден в ответе"
        assert created_booking["booking"]["firstname"] == booking_data["firstname"], "Заданное имя не совпадает"
        assert created_booking["booking"]["totalprice"] == booking_data["totalprice"], "Заданная стоимость не совпадает"

        # Проверяем, что бронирование можно получить по ID
        get_booking = auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        assert get_booking.status_code == 200, "Бронь не найдена"
        assert get_booking.json()["lastname"] == booking_data["lastname"], "Заданная фамилия не совпадает"

        # Обновляем бронирование
        update_response = auth_session.put(f"{BASE_URL}/booking/{booking_id}", json=update_booking_data)
        assert update_response.status_code == 200, "Ошибка при обновлении брони"

        # Проверяем, что данные бронирования обновились
        update_booking = auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        updated_data = update_booking.json()
        assert update_booking.status_code == 200, "Бронь не найдена"
        assert updated_data["firstname"] == update_booking_data["firstname"]
        assert updated_data["lastname"] == update_booking_data["lastname"]
        assert updated_data["totalprice"] == update_booking_data["totalprice"]
        assert updated_data["bookingdates"]["checkin"] == update_booking_data["bookingdates"]["checkin"]
        assert updated_data["additionalneeds"] == update_booking_data["additionalneeds"]

    def test_partial_update_booking(self, auth_session, created_booking, booking_data, partial_update_booking_data):
        # Создаём бронирование и проверяем его доступность
        booking_id = created_booking.get("bookingid")
        assert booking_id is not None, "Идентификатор брони не найден в ответе"
        assert created_booking["booking"]["firstname"] == booking_data["firstname"], "Заданное имя не совпадает"
        assert created_booking["booking"]["totalprice"] == booking_data["totalprice"], "Заданная стоимость не совпадает"

        # Проверяем, что бронирование можно получить по ID
        get_booking = auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        assert get_booking.status_code == 200, "Бронь не найдена"
        assert get_booking.json()["lastname"] == booking_data["lastname"], "Заданная фамилия не совпадает"

        # Обновляем бронирование
        update_response = auth_session.patch(f"{BASE_URL}/booking/{booking_id}", json=partial_update_booking_data)
        assert update_response.status_code == 200, "Ошибка при обновлении брони"

        # Проверяем, что данные бронирования обновились
        update_booking = auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        updated_data = update_booking.json()
        assert updated_data["firstname"] != booking_data["firstname"]
        assert updated_data["lastname"] != booking_data["lastname"]
        assert updated_data["totalprice"] == booking_data["totalprice"]
        assert updated_data["bookingdates"]["checkin"] == booking_data["bookingdates"]["checkin"]
        assert updated_data["additionalneeds"] == booking_data["additionalneeds"]


class TestNegativeBookings:
    def test_negative_types_create_booking(self, auth_session, invalid_booking_data_types):
        # Создаём бронирования с некорректными данными
        create_invalid_booking = auth_session.post(f"{BASE_URL}/booking", json=invalid_booking_data_types)
        assert create_invalid_booking.status_code == 500, "Ожидается ошибка"

    def test_negative_fields_create_booking(self, auth_session, invalid_booking_data_fields):
        # Создаём бронирования с некорректными данными
        create_invalid_booking = auth_session.post(f"{BASE_URL}/booking", json=invalid_booking_data_fields)
        assert create_invalid_booking.status_code == 500, "Ожидается ошибка"

    def test_negative_update_non_existent_booking(self, auth_session, update_booking_data):
        # Обновляем бронирование
        update_response = auth_session.put(f"{BASE_URL}/booking/99999999999999999999999", json=update_booking_data)
        assert update_response.status_code == 405

    def test_negative_delete_booking(self, invalid_auth_session, created_booking, booking_data):
        # Создаём бронирование и проверяем его доступность
        booking_id = created_booking.get("bookingid")
        assert booking_id is not None, "Идентификатор брони не найден в ответе"
        assert created_booking["booking"]["firstname"] == booking_data["firstname"], "Заданное имя не совпадает"
        assert created_booking["booking"]["totalprice"] == booking_data["totalprice"], "Заданная стоимость не совпадает"

        # Проверяем, что бронирование можно получить по ID
        get_booking = invalid_auth_session.get(f"{BASE_URL}/booking/{booking_id}")
        assert get_booking.status_code == 200, "Бронь не найдена"
        assert get_booking.json()["lastname"] == booking_data["lastname"], "Заданная фамилия не совпадает"

        # Удаляем бронирование
        deleted_booking = invalid_auth_session.delete(f"{BASE_URL}/booking/{booking_id}")
        assert deleted_booking.status_code == 403