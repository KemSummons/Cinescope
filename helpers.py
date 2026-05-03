def assert_common_fields_equal(expected, actual, debug=False, exclude_fields=None):
    exclude_fields = set(exclude_fields or [])
    expected_data = expected.model_dump() if hasattr(expected, "model_dump") else expected
    actual_data = actual.model_dump() if hasattr(actual, "model_dump") else actual

    common_fields = (expected_data.keys() & actual_data.keys()) - exclude_fields
    assert common_fields, "У моделей нет общих полей для сравнения"

    for field in common_fields:
        if debug:
            print(
                f'compare field="{field}": '
                f'expected={expected_data[field]!r}, actual={actual_data[field]!r}'
            )

        assert expected_data[field] == actual_data[field], (
            f'Поле "{field}" не совпадает: '
            f'expected={expected_data[field]!r}, actual={actual_data[field]!r}'
        )