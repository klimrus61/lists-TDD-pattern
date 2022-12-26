from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape
from lists.models import Item, List
from lists.forms import (
    DUPLICATE_ITEM_ERROR, EMPTY_ITEM_ERROR,
    ExistingListItemForm, ItemForm,
)
from unittest import skip


class HomePageTest(TestCase):
    """Тест домашней страницы"""

    def test_uses_home_template(self):
        """тест: используется домашний шаблон"""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_uses_item_form(self):
        """тест: домашняя старница использует форму для элемента"""
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)


class ListViewTest(TestCase):
    '''тест: представления списка'''

    def post_invalid_input(self):
        """вспомогательная функция: отправляет недопустимый ввод"""
        list_ = List.objects.create()
        return self.client.post(
            reverse('view_list', args=[list_.id]),
            data={'text': ''}
        )

    def test_for_invalid_input_nothing_saved_to_db(self):
        '''тест на недопустимый ввод: ничего не сохраняется в бд'''
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_list_template(self):
        '''тест на недопустимый ввод: отображается шаблон списка'''
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')

    def test_for_invalid_input_shows_error_on_page(self):
        '''тест на недопустимый ввод: ошибки выводятся на страницу'''
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_duplicate_item_validation_errors_end_up_list_page(self):
        '''тест: ошибки валидации повторяющегося элемента
            оканчиваюся на странице списков'''
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='foo')
        response = self.client.post(
            f"/lists/{list1.id}/",
            data={"text": "foo"}
        )

        expected_error = escape(DUPLICATE_ITEM_ERROR)

        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, "list.html")
        self.assertEqual(Item.objects.all().count(), 1)

    def test_uses_list_template(self):
        '''тест: используется шаблон списка'''
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_only_items_for_that_list(self):
        '''тест: отображаются элементы только этого списка'''
        correct_list = List.objects.create()
        Item.objects.create(text='itemey 1', list=correct_list)
        Item.objects.create(text='itemey 2', list=correct_list)
        other_list = List.objects.create()
        Item.objects.create(text='other itemey 1 other list', list=other_list)
        Item.objects.create(text='other itemey 2 other list', list=other_list)

        response = self.client.get(f'/lists/{correct_list.id}/')

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'other itemey 1 other list')
        self.assertNotContains(response, 'other itemey 2 other list')

    def test_passes_correct_list_to_template(self):
        '''тест: передает правильный список в шаблон'''
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'], correct_list)


    def test_can_save_a_POST_request_to_an_existing_list(self):
        '''тест: может сохранить post-запрос в существующий список'''
        other_list = List.objects.create()
        corrent_list = List.objects.create()

        self.client.post(
            f'/lists/{corrent_list.id}/',
            data={'text': 'A new item for an existing list'},
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, corrent_list)
    
    def test_POST_redirects_to_list_view(self):
        '''тест:post-запрос переадресуется в представление списка'''
        other_list = List.objects.create()
        corrent_list = List.objects.create()

        response = self.client.post(
            f'/lists/{corrent_list.id}/',
            data={'text': 'A new item for an existing list'},
        )

        self.assertRedirects(response, f'/lists/{corrent_list.id}/')

    def test_for_invalid_input_passes_form_to_template(self):
        '''тест на недопустимый ввод: передается форма в шаблон'''
        response = self.post_invalid_input()
        self.assertIsInstance(response.context["form"], ExistingListItemForm)
        
    def test_displays_item_form(self):
        '''тест отображения формы для элемента'''
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertIsInstance(response.context["form"], ExistingListItemForm)
        self.assertContains(response, 'name="text"')


class NewListTest(TestCase):
    '''тест нового списка'''

    def test_can_save_a_POST_request(self):
        """тест: можно сохранить POST запрос"""
        self.client.post('/lists/new', data={"text": 'A new list item'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new list item")
    
    def test_redirects_after_POST(self):
        '''тест: переадресует после post-запроса'''
        response = self.client.post('/lists/new', data={"text": 'A new list item'})
        new_list = List.objects.first()
        self.assertRedirects(response, f'/lists/{new_list.id}/')

    def test_for_invalid_input_renders_home_template(self):
        '''тест на недопустимый ввод: отображает домашний шаблон'''
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_validation_errors_are_shown_on_home_page(self):
        '''тест: ошибки валидации выводятся на домашней странице'''
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_for_invalid_input_passes_form_to_template(self):
        '''тест на недопустимый ввод: форма передается в шаблон'''
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertIsInstance(response.context['form'], ItemForm)
    
    def test_invalid_list_items_arent_saved(self):
        '''тест: недопустимые элементы списка не сохраняются'''
        self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)


class MyListsTest(TestCase):
    '''тест пользовательских списков'''

    def test_my_lists_url_renders_my_lists_template(self):
        response = self.client.get('/lists/users/a@b.com/')
        self.assertTemplateUsed(response, 'my_lists.html')
