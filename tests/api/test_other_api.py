import allure
import pytest
import logging
from sqlalchemy.orm import Session
from db_models.models import AccountTransactionTemplate
from utils.data_generator import DataGenerator

logger = logging.getLogger(__name__)


@allure.epic("Тестирование транзакций")
@allure.feature("Тестирование транзакций между счетами")
@pytest.mark.db
class TestAccountTransactionTemplate:

    @allure.story("Корректность перевода денег между двумя счетами")
    @allure.description("""
        Этот тест проверяет корректность перевода денег между двумя счетами.
        Шаги:
        1. Создание двух счетов: Stan и Bob.
        2. Перевод 200 единиц от Stan к Bob.
        3. Проверка изменения балансов.
        4. Очистка тестовых данных.
        """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("qa_name", "Ivan Petrovich")
    @allure.title("Тест перевода денег между счетами - 200 рублей")
    def test_accounts_transaction_template(self, db_session: Session):
        with allure.step("Создание тестовых данных в базе данных: счета Stan и Bob"):
            stan = AccountTransactionTemplate(user=f"Stan_{DataGenerator.generate_random_int(1000)}", balance=1000)
            bob = AccountTransactionTemplate(user=f"Bob_{DataGenerator.generate_random_int(1000)}", balance=500)
            logger.info("🧪 [START] Тест: accounts_transaction_template")
            logger.info(f"💰 Начальные балансы: {stan.user}={stan.balance}, {bob.user}={bob.balance}")
            db_session.add_all([stan, bob])
            db_session.commit()

        @allure.step("Функция перевода денег: transfer_money")
        @allure.description("""
            функция выполняющая транзакцию, имитация вызова функции на стороне тестируемого сервиса
            и вызывая метод transfer_money, мы как будто бы делаем запрос в api_manager.movies_api.transfer_money
            """)
        def transfer_money(session, from_account, to_account, amount):
            with allure.step("Получаем счета"):
                from_account = session.query(AccountTransactionTemplate).filter_by(user=from_account).one()
                to_account = session.query(AccountTransactionTemplate).filter_by(user=to_account).one()
                logger.info(f"💸 Запрос перевода: {amount} ед. от '{from_account.user}' к '{to_account.user}'")

            with allure.step("Проверяем, что на счете достаточно средств"):
                if from_account.balance < amount:
                    raise ValueError("Недостаточно средств на счете")

            with allure.step("Выполняем перевод"):
                from_account.balance -= amount
                to_account.balance += amount

            with allure.step("Сохраняем изменения"):
                session.commit()

            logger.info(f"📊 Обновление балансов: {from_account.user} - {from_account.balance}, {to_account.user} - {to_account.balance}")

        with allure.step("Проверяем начальные балансы"):
            assert stan.balance == 1000
            assert bob.balance == 500

        try:
            with allure.step("Выполняем перевод 200 единиц от stan к bob"):
                transfer_money(db_session, from_account=stan.user, to_account=bob.user, amount=200)

            with allure.step("Проверяем, что балансы изменились"):
                assert stan.balance == 800
                assert bob.balance == 700

        except Exception as e:
            with allure.step("ОШИБКА! Откаты транзакции"):
                db_session.rollback()

            pytest.fail(f"Ошибка при переводе денег: {e}")

        finally:
            with allure.step("Удаляем данные для тестирования из базы"):
                db_session.delete(stan)
                db_session.delete(bob)
                db_session.commit()
