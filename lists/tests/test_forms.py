from unittest import TestCase as UnitTestCase
from unittest.mock import patch, Mock
from django.test import TestCase
from lists.forms import (
    DUPLICATE_ITEM_ERROR, EMPTY_ITEM_ERROR,
    ExistingListItemForm, ItemForm, NewListForm
)
from lists.models import Item, List


class ItemFormTest(TestCase):
    '''тест формы для элемента списка'''

    def test_form_renders_item_text_input(self):
        '''тест: форма отображает текстовое поле ввода'''
        form = ItemForm()
        # self.fail(form.as_p())
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control input-lg"', form.as_p())

    def test_form_validation_for_blank_items(self):
        '''тест валидации формы для пустых элементов'''
        form = ItemForm(data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['text'],
            [EMPTY_ITEM_ERROR]
        )

class ExistingListItemFormTest(TestCase):
    '''тест формы элемента существующего списка'''
    
    def test_form_renders_item_text_input(self):
        '''тест: форма отбражает текстовый ввод элемента'''
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_)
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())

    def test_form_validation_for_blank_items(self):
        """тест: валидация формы для пустых элементов"""
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [EMPTY_ITEM_ERROR])

    def test_form_validation_for_duplicate_items(self):
        '''тест: валидация формы для повторяющихся элементов'''
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='no twins!')
        form = ExistingListItemForm(for_list=list_, data={'text': 'no twins!'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [DUPLICATE_ITEM_ERROR])

    
    def test_form_save(self):
        '''тест: сохранения формы'''
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={'text': 'foo'})
        new_item = form.save()
        self.assertEqual(new_item, Item.objects.first())

class NewListFormTest(UnitTestCase):
    '''тест форм для нового списка'''

    @patch('lists.forms.List.create_new')
    def test_save_create_new_list_from_post_data_if_user_not_authenticated(
        self, mock_List_create_new
    ):
        '''тест: save создает новый список из POST-данных \
если пользователь не аутентифицирован'''
        user = Mock(is_authenticated=False)
        form = NewListForm(data={'text': 'new item text'})
        form.is_valid()
        form.save(owner=user)
        mock_List_create_new.assert_called_once_with(
            first_item_text='new item text'
        )

    @patch('lists.forms.List.create_new')
    def test_save_create_new_list_with_owner_if_user_authenticated(
        self, mock_List_create_new
    ):
        '''тест: save создает новый с владельцем, \
если пользователь аутентифицирован'''
        user = Mock(is_authenticated=True)
        form = NewListForm(data={'text': 'new item text'})
        form.is_valid()
        form.save(owner=user)
        mock_List_create_new.assert_called_once_with(
            first_item_text='new item text', owner=user
        )
    
    @patch('lists.forms.List.create_new')
    def test_save_returns_new_list_object(self, mock_List_create_new):
        '''тест: save возвращает новый объект списка'''
        user = Mock(is_authenticated=True)
        form = NewListForm(data={'text': 'new item text'})
        form.is_valid()
        response = form.save(owner=user)
        self.assertEqual(response, mock_List_create_new.return_value)