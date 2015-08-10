from unittest import TestCase
from bitcoincrawler.components.bitcoind.model import BTCDBlock, BTCDTransaction, BTCDVin, BTCDVout
from mock import Mock

class TestBTCDBlockModel(TestCase):
    def setUp(self):
        self.block_obj = {"hash" : "000000000000c5e7fb216de3593318708b3372afb511f3824c4a9f7300a39529",
                          "confirmations" : 253627,
                          "size" : 3263,
                          "height" : 115002,
                          "version" : 1,
                          "merkleroot" : "edbcedc2619adbf21cee77ef0b943717da2bbea41c61296b04497e4590df303b",
                          "tx" : [
                              "0128d4ee91f5ccc61ef9ffe868a874f7b38a7e78cb7510cc576de989832d9345",
                              "c2779f92c308780c4eb6c422b7ea474982bd13626b8a9dac093bdaa33e502e9c",
                          ],
                          "time" : 1301068491,
                          "nonce" : 1630218460,
                          "bits" : "1b00f339",
                          "difficulty" : 68977.78463021,
                          "chainwork" : "000000000000000000000000000000000000000000000000257e64bca853cb2b",
                          "previousblockhash" : "0000000000007f51a1c13814ecb9698f56b91b2599552d7c47ec1d5b7517ae81",
                          "nextblockhash" : "0000000000000f246cec2e9f71acc743db66da926a15cd31a2739612c64546dd"
                      }
        self.tx_objs = [{}, {}]
        self.coinbase_obj = [{}]
        self.txs_factory = Mock()

    def test_BTCBlock(self):
        self.sut = BTCDBlock(self.block_obj, self.txs_factory)
        self.txs_factory.get_transactions.side_effect = [(BTCDTransaction(self.tx_objs[0]), BTCDTransaction(self.tx_objs[1])), (BTCDTransaction(tx) for tx in self.tx_objs[0:1])]
        self.assertEqual(self.sut.hash, self.block_obj['hash'])
        self.assertEqual(self.sut.size, self.block_obj['size'])
        self.assertEqual(self.sut.height, self.block_obj['height'])
        self.assertEqual(self.sut.version, self.block_obj['version'])
        self.assertEqual(self.sut.merkleroot, self.block_obj['merkleroot'])
        self.assertEqual(self.sut.nonce, self.block_obj['nonce'])
        self.assertEqual(self.sut.bits, self.block_obj['bits'])
        self.assertEqual(self.sut.time, self.block_obj['time'])
        self.assertEqual(self.sut.difficulty, self.block_obj['difficulty'])
        self.assertEqual(self.sut.chainwork, self.block_obj['chainwork'])
        self.assertEqual(self.sut.previousblockhash, self.block_obj['previousblockhash'])
        self.assertEqual(self.sut.nextblockhash, self.block_obj['nextblockhash'])
        for tx in self.sut.tx:
            self.assertIsInstance(tx, BTCDTransaction)
        coinbase = self.sut.coinbase
        self.assertIsInstance(coinbase, BTCDTransaction)

class TestBTCDTransactionModel(TestCase):
    def setUp(self):
        self.coinbase_obj = {"txid": "0128d4ee91f5ccc61ef9ffe868a874f7b38a7e78cb7510cc576de989832d9345",
                            "version": 1,
                            "vin": [
                                     {
                                      "coinbase": "0439f3001b0104",
                                      "sequence": 4294967295
                                    }
                                ]
                            }
        self.tx_obj = {"txid": "2b3d98ff686feacee27d3d54fb48a889b519d5aa5d269f5e59bcf1a17d04dfff",
                       "version": 1,
                       "vin": [
                           {
                               "txid": "5f3554a28c0189105b5935c0efe47a0a56392cab7053ca4fbf5aaa025110e80e",
                               "scriptSig": {
                                   "hex": "473044022027dea94113e358d7030468a5ab4523adcd1498eb54b5d6bfcea26cc5e750431802203ad0e07be2dd209b254dcfff76e4e2c1b4bba3b8d8b140ef6425dcaae79321b2014104fd359fe2259822af6b02d5b1d97b726c6da0000f8c3df43eb2aa3e84397aa04f7b7b9b867bbcaa8838520756d2768e1f994b5297694ae56eafee661aee550ad2",
                                   "asm": "3044022027dea94113e358d7030468a5ab4523adcd1498eb54b5d6bfcea26cc5e750431802203ad0e07be2dd209b254dcfff76e4e2c1b4bba3b8d8b140ef6425dcaae79321b201 04fd359fe2259822af6b02d5b1d97b726c6da0000f8c3df43eb2aa3e84397aa04f7b7b9b867bbcaa8838520756d2768e1f994b5297694ae56eafee661aee550ad2"
                               },
                               "sequence": 4294967295,
                               "vout": 1
                           }
                       ],
                       "locktime": 0,
                       "vout": [
                           {
                               "value": 19.97,
                               "scriptPubKey": {
                                   "addresses": [
                                       "1FvrEVr7UkPEVmS8pPGRStzm7zoZ21fDs9"
                                   ],
                                   "type": "pubkeyhash",
                                   "reqSigs": 1,
                                   "hex": "76a914a3c0e78347dd1619514cb0e787024f6f4b908eef88ac",
                                   "asm": "OP_DUP OP_HASH160 a3c0e78347dd1619514cb0e787024f6f4b908eef OP_EQUALVERIFY OP_CHECKSIG"
                               },
                               "n": 0
                           },
                           {
                               "value": 2.0,
                               "scriptPubKey": {
                                   "addresses": [
                                       "1PK1dBrhtzps3rpN9E2Hhsy4V4Acxeb51Z"
                                   ],
                                   "type": "pubkeyhash",
                                   "reqSigs": 1,
                                   "hex": "76a914f4bac67efaa32e14873c8372e16f009c85136f8c88ac",
                                   "asm": "OP_DUP OP_HASH160 f4bac67efaa32e14873c8372e16f009c85136f8c OP_EQUALVERIFY OP_CHECKSIG"
                               },
                               "n": 1
                           }
                       ]
                   }

    def tearDown(self):
        pass

    def test_BTCDTransaction_coinbase(self):
        self.sut = BTCDTransaction(self.coinbase_obj, meta={"parent_block": 'block_hash'})
        self.assertIs(self.sut.is_coinbase, True)
        self.assertEqual(self.sut.parent_block, 'block_hash')

    def test_BTCDTransaction_mempool(self):
        self.sut = BTCDTransaction(self.tx_obj)
        self.assertEqual(self.sut.txid, self.tx_obj['txid'])
        self.assertEqual(self.sut.version, self.tx_obj['version'])
        self.assertEqual(self.sut.locktime, self.tx_obj['locktime'])
        self.assertIsNone(self.sut.parent_block)
        for vin in self.sut.vin:
            self.assertIsInstance(vin, BTCDVin)
        for vout in self.sut.vout:
            self.assertIsInstance(vout, BTCDVout)