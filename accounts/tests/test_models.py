from django.test import TestCase
from django.contrib import auth

from accounts.models import Token


User = auth.get_user_model()

class UserModelTest(TestCase):
    '''тест модели пользователя'''

    def test_user_is_valid_with_email_only(self):
        '''тест: пользователь допустим только с электронной почтой'''
        user = User(email='a@b.com')
        user.full_clean() # Не должно поднять исключение
    
    def test_email_is_primary_key(self):
        '''тест: адрес электронной почты является первичным ключом'''
        user = User(email='a@b.com')
        self.assertEqual(user.pk, 'a@b.com')
    
    def test_no_problem_with_auth_login(self):
        '''тест: нет проблем с auth_login'''
        user = User.objects.create(email='klim@example.com')
        user.backend = ''
        request = self.client.request().wsgi_request
        auth.login(request, user) # не должно поднять исключение 


class TokenModelTest(TestCase):
    """тест модели маркера"""

    def test_links_user_with_auto_generated_uid(self):
        """тест: соединяет пользователя с автогенерированным uid"""
        token1 = Token.objects.create(email='a@b.com')
        token2 = Token.objects.create(email='a@b.com')
        self.assertNotEqual(token1.uid, token2.uid)
    
    