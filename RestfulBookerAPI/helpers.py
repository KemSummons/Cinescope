from RestfulBookerAPI.constants import GET_BOOKING_ID_ENDPOINT


def get_booking(requester, booking_id, expected_status=200):
    """Получаем данные по бронированию"""
    response = requester.send_request(
        method="GET",
        endpoint=GET_BOOKING_ID_ENDPOINT.format(id=booking_id),
        expected_status=expected_status,
        need_logging=True
    )
    return response.json() if expected_status == 200 else response
