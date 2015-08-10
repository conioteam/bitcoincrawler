from unittest import TestCase
from mock import Mock
from bitcoincrawler.components.base_factory import AdapterFactory, BaseFactory

class TestAdapterFactory(TestCase):
    def setUp(self):
        self.txs_factory = Mock()
        self.blocks_factory = Mock()
        self.sut = AdapterFactory(self.txs_factory, self.blocks_factory)

    def tearDown(self):
        self.txs_factory.reset_mock()
        self.blocks_factory.reset_mock()

    def test_get_mempool_transactions(self):
        self.txs_factory.get_mempool_transactions.side_effect = ['called']
        self.sut.get_mempool_transactions()
        self.txs_factory.get_mempool_transactions.assert_called_once_with(limit=None)

    def test__get_transaction(self):
        self.txs_factory._get_transaction.side_effect = ['called']
        self.sut._get_transaction('arg')
        self.txs_factory._get_transaction.assert_called_once_with('arg')

    def test_get_transactions(self):
        self.txs_factory.get_transactions.side_effect = ['called']
        self.sut.get_transactions('arg')
        self.txs_factory.get_transactions.assert_called_once_with('arg')

    def test_generate_blocks(self):
        self.blocks_factory.generate_blocks.side_effect = ['called']
        self.sut.generate_blocks()
        self.blocks_factory.generate_blocks.assert_called_once_with(blockhash=None,
                                                                    blockheight=None,
                                                                    stop_blockhash=None,
                                                                    stop_blockheight=None,
                                                                    max_iterations=None,
                                                                    txs_factory=self.txs_factory)

class TestBaseFactory(TestCase):
    def setUp(self):
        self.sut = BaseFactory()

    def test__get_transaction(self):
        with self.assertRaises(NotImplementedError):
            self.sut._get_transaction(None)

    def test_get_mempool_transactions(self):
        with self.assertRaises(NotImplementedError):
            self.sut.get_mempool_transactions()

    def test_get_transactions(self):
        with self.assertRaises(NotImplementedError):
            self.sut.get_transactions(None)

    def test_generate_blocks(self):
        with self.assertRaises(NotImplementedError):
            self.sut.generate_blocks(None)

