import re
from django.core import mail
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest


TEST_EMAIL = 'klim@example.com'
SUBJECT = 'Your login link for Superlists'

class LoginTest(FunctionalTest):
    '''тест регистрации в системе'''

    def test_can_get_email_link_to_log_in(self):
        '''тест: можно получить ссылку по почте для регистрации'''

        # Соня заходит на офигенный сайт суперсписков и впервые
        # замечает раздел "войти" в новигационной панели
        # Он говорит ей ввести свой адрес электронной почты, что она и делает
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_name('email').send_keys(TEST_EMAIL)
        self.browser.find_element_by_name('email').send_keys(Keys.ENTER)

        # Появляется сообщение, которое говорит, что ей на почту 
        # было отправленно электронное письмо

        self.wait_for(lambda: self.assertIn(
            'Check your mail',
            self.browser.find_element_by_tag_name('body').text
        ))

        # Соня проверяет совю почту и находит сообщение
        email = mail.outbox[0]
        self.assertIn(TEST_EMAIL, email.to)
        self.assertEqual(email.subject, SUBJECT)

        # Оно содержит ссылку на url-адрес
        self.assertIn('Use this link to log in', email.body)
        url_search = re.search(r'http://.+/.+$', email.body)
        if not url_search:
            self.fail(f'Could not find url in email body:\n {email.body}')
        url = url_search.group(0)
        self.assertIn(self.live_server_url, url)

        # Соня нажимает на ссылку 
        self.browser.get(url)

        # Она зарегистрированна в системе!
        self.wait_for(
            lambda: self.browser.find_element_by_link_text('Log out')
        )
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertIn(TEST_EMAIL, navbar.text)

        # Теперь она выходит из системы
        self.browser.find_element_by_link_text('Log out').click()

        # Вышла из системы
        self.wait_for(
            lambda: self.browser.find_element_by_name('email')
        )
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertNotIn(TEST_EMAIL, navbar.text)