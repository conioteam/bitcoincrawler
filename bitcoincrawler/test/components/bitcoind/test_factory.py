from unittest import TestCase
from unittest.mock import Mock
from bitcoincrawler.components.bitcoind import factory

class TestBitcoinFactory(TestCase):
    def setUp(self):
        client = Mock()

    def tearDown(self):
        pass
