from unittest import TestCase
from bitcoincrawler.components.bitcoind import factory
from bitcoincrawler.test.mocks.components.bitcoind.client import bitcoinCli
from bitcoincrawler.components.bitcoind.model import BTCDTransaction, BTCDBlock, BTCDVin, BTCDVout
from copy import deepcopy

class TestBitcoinFactory(TestCase):
    def setUp(self):
        self.btcd = deepcopy(bitcoinCli)
        self.sut = factory.BitcoindFactory(self.btcd)
        self.async_sut = factory.BitcoindFactory(self.btcd, async=True)

    def tearDown(self):
        self.btcd = deepcopy(bitcoinCli)

    def test_get_mempool_transactions(self):
        transactions = [tx for tx in self.sut.get_mempool_transactions()]
        self.assertEqual(100, len(transactions))
        self.btcd.get_raw_mempool.assert_called_once_with()
        for transaction in transactions:
            self.assertIsInstance(transaction, BTCDTransaction)
            for vin in transaction.vin:
                self.assertIsInstance(vin, BTCDVin)
            for vout in transaction.vout:
                self.assertIsInstance(vout, BTCDVout)

    def test_generate_5_blocks_from_height(self):
        blocks = [block for block in self.sut.generate_blocks(height=115000, max_iterations=5)]
        self.assertEqual(5, len(blocks))

        bl_115000_txs = ["8de81b651caaeba5021ae8459b450dffe71c8a630039efc3d5a699fa055eda78",
                         "3e24580de3f6d75cb77e32472d5b76e14206294e6e82a3e7bb0a1189e363f81a",
                         "7adf1a6b0f66c97b4ce48b026b7a496fd7d495330ef0a026469d12cb49511b4f",
                         "be5b1f1cbb890cbe53ef5689715ee0386cb81aaf47c13f9aba96600b93965e8e",
                         "66c1be44c4e5899af46a3b4142f31f95abab7111e707991bbc98f447a5310b4d"]

        for i, txs in enumerate(blocks[0].tx):
            self.assertEqual(txs.txid, bl_115000_txs[i])

        for block in blocks:
            self.assertIsInstance(block, BTCDBlock)
            for i, transaction in enumerate(block.tx):
                self.assertIsInstance(transaction, BTCDTransaction)
                for vin in transaction.vin:
                    self.assertIsInstance(vin, BTCDVin)
                for vout in transaction.vout:
                    self.assertIsInstance(vout, BTCDVout)
                    
                    
    def test_get_mempool_transactions_async(self):
        transactions = [tx for tx in self.async_sut.get_mempool_transactions()]
        self.assertEqual(100, len(transactions))
        self.btcd.get_raw_mempool.assert_called_once_with()
        for transaction in transactions:
            self.assertIsInstance(transaction, BTCDTransaction)
            for vin in transaction.vin:
                self.assertIsInstance(vin, BTCDVin)
            for vout in transaction.vout:
                self.assertIsInstance(vout, BTCDVout)

    def test_generate_5_blocks_from_height_async(self):
        blocks = [block for block in self.async_sut.generate_blocks(height=115000, max_iterations=5)]
        self.assertEqual(5, len(blocks))

        bl_115000_txs = ["8de81b651caaeba5021ae8459b450dffe71c8a630039efc3d5a699fa055eda78",
                         "3e24580de3f6d75cb77e32472d5b76e14206294e6e82a3e7bb0a1189e363f81a",
                         "7adf1a6b0f66c97b4ce48b026b7a496fd7d495330ef0a026469d12cb49511b4f",
                         "be5b1f1cbb890cbe53ef5689715ee0386cb81aaf47c13f9aba96600b93965e8e",
                         "66c1be44c4e5899af46a3b4142f31f95abab7111e707991bbc98f447a5310b4d"]

        for i, txs in enumerate(blocks[0].tx):
            self.assertEqual(txs.txid, bl_115000_txs[i])

        for block in blocks:
            self.assertIsInstance(block, BTCDBlock)
            for i, transaction in enumerate(block.tx):
                self.assertIsInstance(transaction, BTCDTransaction)
                for vin in transaction.vin:
                    self.assertIsInstance(vin, BTCDVin)
                for vout in transaction.vout:
                    self.assertIsInstance(vout, BTCDVout)