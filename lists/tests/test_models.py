from lists.models import Item, List
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class ListAndItemModelsTest(TestCase):
    '''Тест моделей элемента списка и списка'''
    

    def test_item_is_related_to_list(self):
        '''тест: элемент связан со списком'''
        list_ = List.objects.create()
        item = Item()
        item.list = list_
        item.save()
        self.assertIn(item, list_.item_set.all())

    def test_cannot_save_empty_list_items(self):
        '''тест: нельзя добавлять пустые элементы списка'''
        list_ = List.objects.create()
        item = Item(list=list_, text='')
        with self.assertRaises(ValidationError):
            item.save()
            item.full_clean()
    
    def test_duplicate_items_are_invalid(self):
        '''тест: повторяющиеся элементы не допустимы'''
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='foo')
        with self.assertRaises(ValidationError):
            item = Item(list=list_, text='foo')
            item.full_clean()

    def test_CAN_save_same_item_to_different_lists(self):
        '''тест: МОЖЕТ сохранить тот же элемент в разные списки'''
        list1 = List.objects.create()
        list2 = List.objects.create()
        Item.objects.create(list=list1, text='bla')
        item = Item(list=list2, text='bla')
        item.full_clean() # не должен поднять исключение

    def test_list_ordering(self):
        '''тест: упорядочивание списка'''
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='i1')
        item2 = Item.objects.create(list=list1, text='item 2')
        item3 = Item.objects.create(list=list1, text='i3')
        self.assertEqual(
            list(Item.objects.all()),
            [item1, item2, item3]
        )

    def test_string_representation(self):
        '''тест: строкового представления'''
        item = Item(text='bar')
        self.assertEqual(str(item), 'bar')


class ItemModelTest(TestCase):
    '''тест модели элемента'''
    
    def test_default_text(self):
        '''тест заданного по умолчанию текста'''
        item = Item()
        self.assertEqual(item.text, '')


class ListModelTest(TestCase):
    '''тест модели списка'''

    def test_get_absolute_url(self):
        '''тест: получен обсолютный url'''
        list_ = List.objects.create()
        self.assertEqual(list_.get_absolute_url(), f'/lists/{list_.id}/')

    def test_create_new_creates_list_and_first_item(self):
        '''тест: create_new создает список и первый элемент'''
        List.create_new(first_item_text='new item text')
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'new item text')
        new_list = List.objects.first()
        self.assertEqual(new_item.list, new_list)
    
    def test_create_new_optionally_saves_owner(self):
        '''тест: create_new необязательно сохраняет владельца'''
        user = User.objects.create()
        List.create_new(first_item_text='new item text', owner=user)
        new_list = List.objects.first()
        self.assertEqual(new_list.owner, user)
    
    def test_lists_can_have_owners(self):
        '''тест: списки могут иметь владельца'''
        List(owner=User()) # не должно поднять исключение

    def test_list_owner_is_optional(self):
        '''тест: владелец списка необязательный'''
        List().full_clean() # не должно поднять исключение
    
    def test_create_returns_new_list_object(self):
        '''тест: create возвращает новый объект списка'''
        returned = List.create_new(first_item_text='new item text')
        new_list = List.objects.first()
        self.assertEqual(returned, new_list)

    def test_list_name_is_first_item_text(self):
        '''тест: имя списка является текстом первого элемента'''
        list_ = List.objects.create()
        first_item = Item.objects.create(list=list_, text='first item')
        Item.objects.create(list=list_, text='second item')
        self.assertEqual(list_.name, first_item.text)