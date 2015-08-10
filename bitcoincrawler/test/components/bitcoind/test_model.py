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
        self.tx_objs = [{"txid": "0128d4ee91f5ccc61ef9ffe868a874f7b38a7e78cb7510cc576de989832d9345",
                         "version": 1,
                         "vin": [
                             {
                                 "coinbase": "0439f3001b0104",
                                 "sequence": 4294967295
                             }
                         ],
                         "locktime": 0,
                         "vout": [
                             {
                                 "value": 50.02,
                                 "scriptPubKey": {
                                     "addresses": [
                                         "13KqR1m6nZa8VjjACv9cvrrTCGYPMnFStG"
                                     ],
                                     "type": "pubkey",
                                     "reqSigs": 1,
                                     "hex": "41048afaeb6f604e026cde21504f44eee148fb6516dc696bb795a31e6d8b5d1206f6af1d9692ee92185a3b3238119ff81c49734ff97f44993e82eb4efb83a43c3830ac",
                                     "asm": "048afaeb6f604e026cde21504f44eee148fb6516dc696bb795a31e6d8b5d1206f6af1d9692ee92185a3b3238119ff81c49734ff97f44993e82eb4efb83a43c3830 OP_CHECKSIG"
                                 },
                                 "n": 0
                                 }
                             ]
                         },
                         {"txid": "0128d4ee91f5ccc61ef9ffe868a874f7b38a7e78cb7510cc576de989832d9345",
                          "version": 1,
                          "vin": [
                              {
                                  "coinbase": "0439f3001b0104",
                                  "sequence": 4294967295
                              }
                          ],
                          "locktime": 0,
                          "vout": [
                              {
                                  "value": 50.02,
                                  "scriptPubKey": {
                                      "addresses": [
                                          "13KqR1m6nZa8VjjACv9cvrrTCGYPMnFStG"
                                      ],
                                      "type": "pubkey",
                                      "reqSigs": 1,
                                      "hex": "41048afaeb6f604e026cde21504f44eee148fb6516dc696bb795a31e6d8b5d1206f6af1d9692ee92185a3b3238119ff81c49734ff97f44993e82eb4efb83a43c3830ac",
                                      "asm": "048afaeb6f604e026cde21504f44eee148fb6516dc696bb795a31e6d8b5d1206f6af1d9692ee92185a3b3238119ff81c49734ff97f44993e82eb4efb83a43c3830 OP_CHECKSIG"
                                  },
                                  "n": 0
                                  }
                              ]
                          }]
        self.coinbase_obj = [{"txid": "0128d4ee91f5ccc61ef9ffe868a874f7b38a7e78cb7510cc576de989832d9345",
                           "version": 1,
                           "vin": [
                               {
                                   "coinbase": "0439f3001b0104",
                                   "sequence": 4294967295
                               }
                           ],
                           "locktime": 0,
                           "vout": [
                               {
                                   "value": 50.02,
                                   "scriptPubKey": {
                                       "addresses": [
                                           "13KqR1m6nZa8VjjACv9cvrrTCGYPMnFStG"
                                       ],
                                       "type": "pubkey",
                                       "reqSigs": 1,
                                       "hex": "41048afaeb6f604e026cde21504f44eee148fb6516dc696bb795a31e6d8b5d1206f6af1d9692ee92185a3b3238119ff81c49734ff97f44993e82eb4efb83a43c3830ac",
                                       "asm": "048afaeb6f604e026cde21504f44eee148fb6516dc696bb795a31e6d8b5d1206f6af1d9692ee92185a3b3238119ff81c49734ff97f44993e82eb4efb83a43c3830 OP_CHECKSIG"
                                   },
                                   "n": 0
                               }
                           ]
                       }]
        self.txs_factory = Mock()

    def test_BTCBlock(self):
        self.sut = BTCDBlock(self.block_obj, self.txs_factory)
        self.txs_factory.get_transactions.side_effect = [(BTCDTransaction(self.tx_objs[0]), BTCDTransaction(self.tx_objs[1])), (BTCDTransaction(tx) for tx in self.tx_objs[0:1])]
        self.assertEqual(self.sut.confirmations, self.block_obj['confirmations'])
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