from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class NewVisitorTest(FunctionalTest):
    """тест новоого посетителя"""

    def test_can_start_a_list_and_retrieve_it_later(self):

        # Соня слышала про крутое новое онлайн-приложение со списком
        # неотложных дел. Она решает оценить его домашнюю страницу
        self.browser.get(self.live_server_url)

        # Она видит, что заголовок и шапка страницы говорят о списках
        # неотложных дел
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        # Ей сразу же предлагается ввести элемент списка
        inputbox = self.get_item_input_box()
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Enter a to-do item'
        )

        # Она набирает в текстовом поле "Купить павлиньи перья" (ее хобби -
        # вязание рыболовных мушек)
        inputbox.send_keys('Купить павлиньи перья')

        # Когда она нажимает enter, страница обновляется, и теперь страница
        # содержит "1: Купить павлиньи перья" в качестве элемента списка
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Купить павлиньи перья')

        # Текстовое поле по-прежнему приглашает ее добавить еще 1 элемент.
        # Она вводит "Сделать мушку из павлиньих перьев"
        # (Соня очень методична)
        inputbox = self.get_item_input_box()
        inputbox.send_keys('Сделать мушку из павлиньих перьев')
        inputbox.send_keys(Keys.ENTER)
        
        # Страница снова обновляется, и теперь показывает оба элемента ее списка
        self.wait_for_row_in_list_table('1: Купить павлиньи перья')
        self.wait_for_row_in_list_table('2: Сделать мушку из павлиньих перьев')

        # Соне интересно, запомнит ли сайт ее список. Далее она видит, что
        # сайт сгенерировал для нее уникальныйы URL-адресс - об этом
        # выводится небольшой текст с обьяснениями.
      

        # Она посещает этот URL-адрес - ее список по-прежнему там.

        # Удовлетворенная, она снова ложится спать

    def test_multiple_users_can_start_lists_at_different_urls(self):
        '''тесть: многочисленные пользователи могут начать списки по разным URL адрессам'''
        # Соня начинает новый список 
        self.browser.get(self.live_server_url)
        inputbox = self.get_item_input_box()
        inputbox.send_keys('Купить павлиньи перья')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Купить павлиньи перья')

        # Она замечает, что список имеет уникальный URL-адресс
        sonya_list_url = self.browser.current_url
        self.assertRegex(sonya_list_url, '/lists/.+')

        # Теперь новый пользователь, Клим, переходит на сайт

        ## Мы используем новый сеанс браузера, тем самым обеспечивая, чтобы никакая
        ## информация от Эдит не прошла через данные cookie и пр.
        self.browser.quit()
        self.browser = webdriver.Firefox()

        # Клим посещает домашнюю страницу. Нет никаких признаков Сони.
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Купить павлиньи перья', page_text)
        self.assertNotIn('Сделать мушку', page_text)

        # Клим начинает новый список, вводя новый элемент. Он менее интересен, чем список Сони
        inputbox = self.get_item_input_box()
        inputbox.send_keys('Купить молоко')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Купить молоко')

        # Клим получает уникальный URL-адресс
        klim_list_url = self.browser.current_url
        self.assertRegex(klim_list_url, '/lists/.+')
        self.assertNotEqual(klim_list_url, sonya_list_url)

        # Нет и следа от списка Сони
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Купить павлиньи перья', page_text)
        self.assertIn('Купить молоко', page_text)

        # Довольные они ложаться спать
