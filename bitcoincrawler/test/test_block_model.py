from unittest import TestCase
from unittest.mock import Mock
import asyncio as asyncio
from bitcoincrawler.components.bitcoind.model import BTCDBlock

class TestBlockModel(TestCase):
    @asyncio.coroutine
    def __async_get_tx(self, tx, **kwargs):
        return self.__get_tx(tx, **kwargs)

    def __get_tx(self, tx, **kwargs):
        return self.tx[0] if tx == "72a49ff05829f6c31a089a9c7413498cb18190ffc839208e67a27cc15933a298" else self.tx[1]

    def setUp(self):
        self.json = \
            {
                "hash" : "000000002ce019cc4a8f2af62b3ecf7c30a19d29828b25268a0194dbac3cac50",
                "confirmations" : 509819,
                "size" : 190,
                "height" : 100,
                "version" : 1,
                "merkleroot" : "72a49ff05829f6c31a089a9c7413498cb18190ffc839208e67a27cc15933a298",
                "tx" : [
                    "72a49ff05829f6c31a089a9c7413498cb18190ffc839208e67a27cc15933a298",
                    "00a49ff05829f6c31a089a9c7413498cb18190ffc839208e67a27cc15933a298"
                ],
                "time" : 1296699105,
                "nonce" : 1811859200,
                "bits" : "1d00ffff",
                "difficulty" : 1.00000000,
                "chainwork" : "0000000000000000000000000000000000000000000000000000006500650065",
                "previousblockhash" : "000000004929c1f4a8affb754235f2cd0f037fa4301360d886779bd5a1e63b2f",
                "nextblockhash" : "00000000e38816ab3892339d43ae31fafd3d4e633f2d909c236b2d209343040e"
            }
        self.tx1 = Mock()
        self.tx = [self.tx1, Mock()]
        self.node_backend = Mock()

    def tearDown(self):
        for tx in self.tx:
            tx.reset_mock()

        self.node_backend.reset_mock()

    def test_block(self):
        block = BTCDBlock(self.json, self.node_backend)
        self.node_backend.get_transaction.side_effect = self.__get_tx
        self.check_block(block)

    def test_block_async(self):
        block = AsyncBTCDBlock(self.json, self.node_backend)
        self.node_backend.get_transaction.side_effect = self.__async_get_tx
        self.check_block(block)

    def check_block(self, block):
        self.assertEqual(190, block.size)
        self.assertEqual(509819, block.confirmations)
        self.assertEqual(100, block.height)
        self.assertEqual(1, block.version)
        self.assertEqual("000000002ce019cc4a8f2af62b3ecf7c30a19d29828b25268a0194dbac3cac50", block.hash)
        self.assertEqual("72a49ff05829f6c31a089a9c7413498cb18190ffc839208e67a27cc15933a298", block.merkleroot)
        self.assertEqual(1296699105, block.time)
        self.assertEqual(1811859200, block.nonce)
        self.assertEqual("1d00ffff", block.bits)
        self.assertEqual(1.0, block.difficulty)
        self.assertEqual("0000000000000000000000000000000000000000000000000000006500650065", block.chainwork)
        self.assertEqual("000000004929c1f4a8affb754235f2cd0f037fa4301360d886779bd5a1e63b2f", block.previousblockhash)
        self.assertEqual("00000000e38816ab3892339d43ae31fafd3d4e633f2d909c236b2d209343040e", block.nextblockhash)

        self.assertEqual(self.tx, [tx for tx in block.tx])

        self.assertEqual(self.tx1, block.coinbase)
