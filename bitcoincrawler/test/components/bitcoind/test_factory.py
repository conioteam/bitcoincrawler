from unittest import TestCase
from bitcoincrawler.components.bitcoind.factory import BitcoindFactory
from bitcoincrawler.components.bitcoind.model import BTCDTransaction, BTCDBlock, BTCDVin, BTCDVout
from types import GeneratorType

import json
from decimal import Decimal
from mock import Mock

class TestBitcoindFactory(TestCase):
    def setUp(self):
        self.btcd = Mock()
        self.sut = BitcoindFactory(self.btcd)

    def tearDown(self):
        self.btcd.reset_mock()

    def test_get_mempool_transactions(self):
        response = {"result": ["txid1", "txid2", "txid3"]}
        self.btcd.get_raw_mempool.side_effect = [response]
        i, limit = 0, 2
        r = self.sut.get_mempool_transactions(limit=limit)
        self.assertIsInstance(r, GeneratorType)
        self.btcd.get_raw_mempool.assert_called_once_with()
        for i, x in enumerate(r):
            self.assertIsInstance(x, BTCDTransaction)
        self.assertEqual(i+1, limit)

    def test_get_transactions(self):
        request = ["txid1", "txid2", "txid3"]
        get_raw_transactions_response = [{"result": "rawtx1"},
                                         {"result":"rawtx2"},
                                         {"result": "rawtx3"}]
        decode_raw_transactions_response = [{"result": {"txid": "rawtx1"}},
                                            {"result": {"txid": "rawtx2"}},
                                            {"result": {"txid": "rawtx3"}}]
        i = 0
        self.btcd.get_raw_transaction.side_effect = get_raw_transactions_response
        self.btcd.decode_raw_transaction.side_effect = decode_raw_transactions_response
        r = self.sut.get_transactions(request)
        self.assertIsInstance(r, GeneratorType)
        for i, x in enumerate(r):
            self.assertIsInstance(x, BTCDTransaction)
            self.assertEqual(x.txid, decode_raw_transactions_response[i]['result']['txid'])
        self.assertEqual(i+1, len(request))

    def test_blocks_generator_multiple_starts(self):
         with self.assertRaises(ValueError):
            self.sut.generate_blocks(blockhash='cafe', blockheight=1)

    def test_blocks_generator_no_starts(self):
         with self.assertRaises(ValueError):
            self.sut.generate_blocks()

    def test_blocks_generator_multiple_stops_height_and_iterations(self):
         with self.assertRaises(ValueError):
            self.sut.generate_blocks(max_iterations=1, stop_blockheight=10)

    def test_blocks_generator_multiple_stops_hash_and_iterations(self):
         with self.assertRaises(ValueError):
            self.sut.generate_blocks(max_iterations=1, stop_blockhash='cafe')

    def test_blocks_generator_multiple_stops_hash_and_height(self):
         with self.assertRaises(ValueError):
            self.sut.generate_blocks(stop_blockhash=1, stop_blockheight=10)

    