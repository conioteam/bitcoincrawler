from unittest import TestCase
from bitcoincrawler.components.pybitcointools.model import PyBitcoinToolsTransaction, PyBitcoinToolsVin, \
    PyBitcoinToolsVout
from mock import Mock
import json
from decimal import Decimal

class TestBTCDTransactionModel(TestCase):
    def setUp(self):
        self.btcd_coinbase_obj = {"txid": "0128d4ee91f5ccc61ef9ffe868a874f7b38a7e78cb7510cc576de989832d9345",
                            "version": 1,
                            "vin": [
                                     {
                                      "coinbase": "0439f3001b0104",
                                      "sequence": 4294967295
                                    }
                                ]
                            }
        self.raw_coinbase = '01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff070439' \
                            'f3001b0104ffffffff018076242a010000004341048afaeb6f604e026cde21504f44eee148fb6516dc696bb7' \
                            '95a31e6d8b5d1206f6af1d9692ee92185a3b3238119ff81c49734ff97f44993e82eb4efb83a43c3830ac0000' \
                            '0000'

        self.btcd_tx_obj = {"txid": "2b3d98ff686feacee27d3d54fb48a889b519d5aa5d269f5e59bcf1a17d04dfff",
                       "version": 1,
                       "vin": [
                           {}
                       ],
                       "locktime": 0,
                       "vout": [
                           {}
                       ]
                   }
        self.raw_tx = '01000000010ee8105102aa5abf4fca5370ab2c39560a7ae4efc035595b1089018ca254355f010000008a473044022' \
                      '027dea94113e358d7030468a5ab4523adcd1498eb54b5d6bfcea26cc5e750431802203ad0e07be2dd209b254dcfff' \
                      '76e4e2c1b4bba3b8d8b140ef6425dcaae79321b2014104fd359fe2259822af6b02d5b1d97b726c6da0000f8c3df43' \
                      'eb2aa3e84397aa04f7b7b9b867bbcaa8838520756d2768e1f994b5297694ae56eafee661aee550ad2ffffffff0240' \
                      'cd0777000000001976a914a3c0e78347dd1619514cb0e787024f6f4b908eef88ac00c2eb0b000000001976a914f4b' \
                      'ac67efaa32e14873c8372e16f009c85136f8c88ac00000000'


    def test_BTCDTransaction_coinbase(self):
        self.sut = PyBitcoinToolsTransaction(self.raw_coinbase, 'txid', meta={"parent_block": 'block_hash'})
        self.assertIs(self.sut.is_coinbase, True)
        self.assertEqual(self.sut.parent, 'block_hash')

    def test_BTCDTransaction_mempool(self):
        self.sut = PyBitcoinToolsTransaction(self.raw_tx, self.btcd_tx_obj['txid'])
        self.assertEqual(self.sut.txid, self.btcd_tx_obj['txid'])
        self.assertEqual(self.sut.version, self.btcd_tx_obj['version'])
        self.assertEqual(self.sut.locktime, self.btcd_tx_obj['locktime'])
        self.assertIsNone(self.sut.parent)
        for vin in self.sut.vin:
            self.assertIsInstance(vin, PyBitcoinToolsVin)
        for vout in self.sut.vout:
            self.assertIsInstance(vout, PyBitcoinToolsVout)

class TestBTCDVin(TestCase):
    def setUp(self):
        self.pybtcd_vin = {'sequence': 4294967295,
                           'outpoint':
                               {'index': 0,
                                'hash': 'c2779f92c308780c4eb6c422b7ea474982bd13626b8a9dac093bdaa33e502e9c'},
                           'script': '473044022075d260edc3d03ba53054243d8f1b928c9e6264eb86766406158679630f2494a502200b015706401a51027bc0c23fce2736547603439be01e979967ef169e2a24bed90141043bdf633e67cf021a7ee69374a213f5f2dc131ca0ba9e75a30d8f1b3d45b29d35e438eb3fe227cb8eda5918e2b66d39c9ccc58f174f7e3ce75f1cf608130e28c4'
                           }

        self.btcd_json_vin = { "txid" : "c2779f92c308780c4eb6c422b7ea474982bd13626b8a9dac093bdaa33e502e9c",
                               "vout" : 0,
                               "scriptSig" : {
                                   "asm" : "3044022075d260edc3d03ba53054243d8f1b928c9e6264eb86766406158679630f2494a502200b015706401a51027bc0c23fce2736547603439be01e979967ef169e2a24bed901 043bdf633e67cf021a7ee69374a213f5f2dc131ca0ba9e75a30d8f1b3d45b29d35e438eb3fe227cb8eda5918e2b66d39c9ccc58f174f7e3ce75f1cf608130e28c4",
                                   "hex" : "473044022075d260edc3d03ba53054243d8f1b928c9e6264eb86766406158679630f2494a502200b015706401a51027bc0c23fce2736547603439be01e979967ef169e2a24bed90141043bdf633e67cf021a7ee69374a213f5f2dc131ca0ba9e75a30d8f1b3d45b29d35e438eb3fe227cb8eda5918e2b66d39c9ccc58f174f7e3ce75f1cf608130e28c4"
                               },
                               "sequence" : 4294967295
                           }

        self.pybtcd_coinbase_vin = {'sequence': 31519,
                                    'outpoint': {
                                        'index': 4294967295,
                                        'hash': '0000000000000000000000000000000000000000000000000000000000000000'
                                    },
                                    'script': '0388a305e4b883e5bda9e7a59ee4bb99e9b1bcfabe6d6de9c8919b014a05a0b4747f0d5ca77212f594b8a6c91f392e8d92efaa4635cb0f02000000f09f909f4d696e656420627920676c6163696572323031350000000000000000000000000000000000'
                                    }

        self.btcd_coinbase_vin = {
            "coinbase" : "0388a305e4b883e5bda9e7a59ee4bb99e9b1bcfabe6d6de9c8919b014a05a0b4747f0d5ca77212f594b8a6c91f392e8d92efaa4635cb0f02000000f09f909f4d696e656420627920676c6163696572323031350000000000000000000000000000000000",
            "sequence" : 31519
        }
        self.parent_tx = Mock()

    def tearDown(self):
        self.parent_tx.reset_mock()

    def test_Vin(self):
        self.sut = PyBitcoinToolsVin(self.pybtcd_vin, self.parent_tx)
        self.assertEqual(self.sut.parent, self.parent_tx)
        self.assertEqual(self.sut.txid, self.btcd_json_vin['txid'])
        self.assertEqual(self.sut.sequence, self.btcd_json_vin['sequence'])
        self.assertEqual(self.sut.vout, self.btcd_json_vin['vout'])
        self.assertEqual(self.sut.scriptSig.hex, self.btcd_json_vin['scriptSig']['hex'])
        self.assertEqual(self.sut.scriptSig.asm, self.btcd_json_vin['scriptSig']['asm'])
        self.assertIsNone(self.sut.coinbase)

    def test_Vin_coinbase(self):
        self.sut = PyBitcoinToolsVin(self.pybtcd_coinbase_vin, self.parent_tx)
        self.assertEqual(self.sut.parent, self.parent_tx)
        self.assertEqual(self.sut.coinbase, self.btcd_coinbase_vin['coinbase'])
        self.assertEqual(self.sut.sequence, self.btcd_coinbase_vin['sequence'])
        self.assertIsNone(self.sut.txid)
        self.assertIsNone(self.sut.vout)
        self.assertIsNone(self.sut.scriptSig.hex)
        self.assertIsNone(self.sut.scriptSig.asm)

class TestBTCDVout(TestCase):
    def setUp(self):
        self.btcd_vout_obj = {"value" : 25.08039992,
                         "n" : 0,
                         "scriptPubKey" : {
                             "asm" : "OP_DUP OP_HASH160 c825a1ecf2a6830c4401620c3a16f1995057c2ab OP_EQUALVERIFY OP_CHECKSIG",
                             "hex" : "76a914c825a1ecf2a6830c4401620c3a16f1995057c2ab88ac",
                             "reqSigs" : 1,
                             "type" : "pubkeyhash",
                             "addresses" : [
                                 "1KFHE7w8BhaENAswwryaoccDb6qcT6DbYY"
                             ]
                         }
                     }
        self.pybtcd_vout_obj = {'script': '76a914c825a1ecf2a6830c4401620c3a16f1995057c2ab88ac', 'value': 2508039992}

        self.parent_tx = Mock()

    def test_Vout(self):
        self.sut = PyBitcoinToolsVout(self.pybtcd_vout_obj, 0, "main", self.parent_tx)
        vout = json.loads(json.dumps(self.btcd_vout_obj), parse_float=Decimal)
        self.assertEqual(self.sut.parent, self.parent_tx)
        self.assertEqual(self.sut.value, vout['value'])
        self.assertEqual(self.sut.n, vout['n'])
        self.assertEqual(self.sut.scriptPubKey.addresses, vout['scriptPubKey']['addresses'])
        self.assertEqual(self.sut.scriptPubKey.type, vout['scriptPubKey']['type'])
        self.assertEqual(self.sut.scriptPubKey.reqSigs, vout['scriptPubKey']['reqSigs'])
        self.assertEqual(self.sut.scriptPubKey.hex, vout['scriptPubKey']['hex'])
        self.assertEqual(self.sut.scriptPubKey.asm, vout['scriptPubKey']['asm'])
