
from selenium.webdriver.common.keys import Keys
from .base import FunctionalTest


class LayoutAndStylingTest(FunctionalTest):
    '''тест макета и стилевого оформления'''

    def test_layout_and_styling(self):
        '''тест макета и стилевого оформления'''
        # Эдит открывает домашнюю страницу
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        # Она замечает, что поле ввода аккуратно центрировано
        inputbox = self.get_item_input_box()
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10
        )
