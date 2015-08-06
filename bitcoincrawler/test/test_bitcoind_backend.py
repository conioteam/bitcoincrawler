from unittest import TestCase
from unittest.mock import Mock
from bitcoincrawler.components.bitcoind.factory import BitcoindFactory

class TestBitcoindBackend(TestCase):
    def fake_get_block(self, hash):
        height = int(hash.split('_')[1])

        nextblockhash = None if height >= 150 else "HASH_{}".format(height + 1)

        return {
                "hash": hash,
                "nextblockhash": nextblockhash,
                "height": height}

    def fake_get_raw_mempool(self):
        return [
            "fake_tx_id_1",
            "fake_tx_id_2",
            "fake_tx_id_3"
        ]

    def fake_get_and_decode_transaction(self, tx):
        num_tx = tx.split('_')[3]
        return {
            "txid": tx
        }

    def setUp(self):
        self.cli = Mock()
        self.cli.get_block_hash.side_effect = lambda x: "HASH_{}".format(x)
        self.cli.get_block.side_effect = self.fake_get_block
        self.cli.get_raw_mempool.side_effect = self.fake_get_raw_mempool
        self.cli.get_and_decode_transaction.side_effect = self.fake_get_and_decode_transaction

        self.sut = BitcoindFactory(self.cli)

    def tearDown(self):
        self.cli.reset_mock()

    def test_generate_from_height_to_height(self):
        blocks = list(self.sut.generate_blocks(height=100, stop_height=120))

        self.assertEquals(21, len(blocks))

        height = 100
        for b in blocks:
            self.assertEquals(height, b.height)
            self.assertEquals("HASH_{}".format(height), b.hash)
            height += 1

    def test_generate_from_hash_to_hash(self):
        blocks = list(self.sut.generate_blocks(hash="HASH_100", stop_hash="HASH_120"))

        self.assertEquals(21, len(blocks))

        height = 100
        for b in blocks:
            self.assertEquals(height, b.height)
            self.assertEquals("HASH_{}".format(height), b.hash)
            height += 1

    def test_num_iterations(self):
        blocks = list(self.sut.generate_blocks(hash="HASH_100", max_iterations=21))

        self.assertEquals(21, len(blocks))

        height = 100
        for b in blocks:
            self.assertEquals(height, b.height)
            self.assertEquals("HASH_{}".format(height), b.hash)
            height += 1

    def test_full_stop(self):
        blocks = list(self.sut.generate_blocks(hash="HASH_100"))

        self.assertEquals(51, len(blocks))

        height = 100
        for b in blocks:
            self.assertEquals(height, b.height)
            self.assertEquals("HASH_{}".format(height), b.hash)
            height += 1


    def test_get_mempool_transactions(self):
        txs = list(self.sut.get_mempool_transactions())

        self.assertEqual(3, len(txs))

        self.assertEqual('fake_tx_id_1', txs[0].txid)
        self.assertEqual('fake_tx_id_2', txs[1].txid)
        self.assertEqual('fake_tx_id_3', txs[2].txid)
