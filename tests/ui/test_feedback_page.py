import allure
import pytest
from models.page_object_models import CinescopeFeedbackPage, CinescopeLoginPage


@allure.epic("Тестирование UI")
@allure.feature("Тестирование Страницы Feedback")
@pytest.mark.ui
class TestFeedbackPage:
    @allure.title("Успешное оставление отзыва")
    def test_submit_feedback_by_ui(self, page, registered_user, create_new_movie):
            login_page = CinescopeLoginPage(page)
            login_page.open()
            login_page.login(registered_user['email'], registered_user['password'])  # Осуществляем вход

            login_page.assert_was_redirect_to_home_page()  # Проверка редиректа на домашнюю страницу
            login_page.make_screenshot_and_attach_to_allure()  # Прикрепляем скриншот
            login_page.assert_allert_was_pop_up()  # Проверка появления и исчезновения алерта

            feedback_page = CinescopeFeedbackPage(page)
            feedback_page.open(create_new_movie.id)

            feedback_page.assert_was_redirect_to_movie_page(create_new_movie.id)

            feedback_page.enter_feedback_text('Приемлемо')
            feedback_page.select_movie_rating(4)
            feedback_page.send_feedback()

            feedback_page.make_screenshot_and_attach_to_allure()
            feedback_page.assert_allert_was_pop_up()