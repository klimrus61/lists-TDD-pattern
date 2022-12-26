import re
import os
import imaplib
import email
import time
from django.core import mail
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest



SUBJECT = 'Your login link for Superlists'

class LoginTest(FunctionalTest):
    '''тест регистрации в системе'''

    def test_can_get_email_link_to_log_in(self):
        '''тест: можно получить ссылку по почте для регистрации'''

        # Соня заходит на офигенный сайт суперсписков и впервые
        # замечает раздел "войти" в новигационной панели
        # Он говорит ей ввести свой адрес электронной почты, что она и делает
        if self.staging_server:
            test_email = 'klimrus61@yandex.ru'
        else:
            test_email = 'klim@example.com'
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_name('email').send_keys(test_email)
        self.browser.find_element_by_name('email').send_keys(Keys.ENTER)

        # Появляется сообщение, которое говорит, что ей на почту 
        # было отправленно электронное письмо

        self.wait_for(lambda: self.assertIn(
            'Check your mail',
            self.browser.find_element_by_tag_name('body').text
        ))

        # Соня проверяет совю почту и находит сообщение
        body = self.wait_for_email(test_email, SUBJECT)

        # Оно содержит ссылку на url-адрес
        self.assertIn('Use this link to log in', body)
        url_search = re.search(r'http://.+/.+$', body)
        if not url_search:
            self.fail(f'Could not find url in email body:\n {body}')
        url = url_search.group(0)
        self.assertIn(self.live_server_url, url)

        # Соня нажимает на ссылку 
        self.browser.get(url)

        # Она зарегистрированна в системе!
        self.wait_to_be_logged_in(email=test_email)

        # Теперь она выходит из системы
        self.browser.find_element_by_link_text('Log out').click()

        # Вышла из системы
        self.wait_to_be_logged_out(email=test_email)
    
    def wait_for_email(self, test_email, subject):
        '''ожидать электронные письма'''
        if not self.staging_server:
            django_mail = mail.outbox[0]
            self.assertIn(test_email, django_mail.to)
            self.assertEqual(django_mail.subject, subject)
            return django_mail.body
        

        mail_pass = os.environ['YANDEX_PASSWORD']
        imap_server = 'imap.yandex.ru'
        imap = imaplib.IMAP4_SSL(imap_server)
        start = time.time()
        try:
            imap.login(test_email, mail_pass)
            res, messeges = imap.select('INBOX')
            messeges = int(messeges[0])
            while time.time() - start < 60:
                for i in range(messeges, messeges - 10, -1):
                    res, msg = imap.fetch(str(i), '(RFC822)')
                    msg = email.message_from_bytes(msg[0][1])
                    if subject in msg["Subject"]:
                        return msg.get_payload()
                time.sleep(5)
        finally:
            imap.close()
            imap.logout()
        