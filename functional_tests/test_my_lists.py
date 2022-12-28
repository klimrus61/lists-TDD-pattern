from django.conf import settings
from .server_tools import create_session_on_server
from .management.commands.create_session import create_pre_authenticated_session
from .base import FunctionalTest
from selenium.common.exceptions import NoSuchElementException


class MyListsTest(FunctionalTest):
    '''тест приложения "Мои списки"'''

    def create_pre_authenticated_session(self, email):
        '''Создать предварительно аунтифицированный сеанс'''
        if self.staging_server:
            session_key = create_session_on_server(self.staging_server, email)
        else:
            session_key = create_pre_authenticated_session(email)
        ## Установить cookie, к-ые нужны для первого посещения домена.
        ## страницы 404 загружаются быстрее всего!
        self.browser.get(self.live_server_url + "/404_no_such_url/")
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session_key,
            path='/',
        ))

    def test_logged_in_users_lists_are_saved_my_lists(self):
        '''тест: списки зарегестрированных пользователей сохраняются \
            как "мои списки"'''

        # Соня является зарегистрированным пользователем
        self.create_pre_authenticated_session('klim@example.com')
        
        # Соня открывает домашнюю страницу и начинает новый список
        self.browser.get(self.live_server_url)
        self.add_list_item('Украсить ёлку')
        self.add_list_item('Приготовить салат')
        first_list_url = self.browser.current_url

        # Она замечает ссылку на "Мои списки" в первый раз.
        self.browser.find_element_by_link_text('My lists').click()

        # Она видит, что ее список находится там, и он назван
        # на основе первого элемента
        self.wait_for(
            lambda: self.browser.find_element_by_link_text('Украсить ёлку')
        )
        self.browser.find_element_by_link_text('Украсить ёлку').click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, first_list_url)
        )

        # Она решает начать еще 1 список, чтобы только убедиться
        self.browser.get(self.live_server_url)
        self.add_list_item('Потанцевать')
        second_list_url = self.browser.current_url

        # Под заголовком "Мои списки" появляется ее новый список
        self.browser.find_element_by_link_text('My lists').click()
        self.wait_for(
            lambda: self.browser.find_element_by_link_text('Потанцевать')
        )
        self.browser.find_element_by_link_text('Потанцевать').click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, second_list_url)
        )

        # Она выходит из системы. Опция "Мои списки" изчезает
        self.browser.find_element_by_link_text("Log out").click()
        try:
            self.wait_for(
                lambda: self.assertEqual(
                    self.browser.find_element_by_link_text('My lists').text,
                    'My lists'
                )
            )
        except NoSuchElementException as e:
            self.assertFalse(False, False)
        else:
            raise Exception('Найден раздел My lists у незарегестрированного user')