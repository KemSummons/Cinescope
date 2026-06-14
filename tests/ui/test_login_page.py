import allure
import pytest
from models.page_object_models import CinescopeLoginPage


@allure.epic("Тестирование UI")
@allure.feature("Тестирование Страницы Login")
@pytest.mark.ui
class TestLoginPage:
   @allure.title("Проведение успешного входа в систему")
   def test_login_by_ui(self, page, registered_user):
       login_page = CinescopeLoginPage(page)# Создаем объект страницы Login

       login_page.open()
       login_page.login(registered_user['email'], registered_user['password']) # Осуществляем вход

       login_page.assert_was_redirect_to_home_page() # Проверка редиректа на домашнюю страницу
       login_page.make_screenshot_and_attach_to_allure() # Прикрепляем скриншот
       login_page.assert_allert_was_pop_up() # Проверка появления и исчезновения алерта