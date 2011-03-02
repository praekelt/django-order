from unittest import TestCase

from order.utils import create_order_classes

class ManagerTestCase(TestCase):
    def test_user_order_by(self):
        pass


class UtilsTestCase(TestCase):
    def test_create_order_classes(self):
        create_order_classes('foo.Bar', ('field1', 'field2'))                
