from unittest import TestCase
from bitcoincrawler.components.pybitcointools.decoders import VINDecoder, VOUTDecoder
from bitcoin import deserialize
import json
from decimal import Decimal

class TestVINDecoder(TestCase):
    def test_Vin_coinbase(self):
        pass

    def test_Vin(self):
        pass

class TestVOUTDecoder(TestCase):
    def test__decode_PayToPubKeyHash(self):
        rawtransaction = "0100000002bc2ea135edf7fe4cbf907601a6dddcaa093c502791b476ebb756a2f63c72ae24000000" \
                         "008c4930460221009d4aa20d971b7c90143750227c905608e9dfe3546a02b25411b3005045e2ba60" \
                         "0221008c52ef6fe58ea64492ee1cde059bb22e0d7eeea2d7130f522c5dc02d598f7b2c0141040277" \
                         "a8116d60b32ddd8fe5e6215e10c39880888a7c7f125fa6815b06a0b51d934cc2b30a3c22e06ff179" \
                         "bca23c54652f233f7665cc54f8b7b1971e894482ea45ffffffffbc2ea135edf7fe4cbf907601a6dd" \
                         "dcaa093c502791b476ebb756a2f63c72ae24010000008c493046022100d4c00f143da46e733e5afe" \
                         "5f8babe61884d6b42250346f9e26f12d5821d70a7d022100b93ae61ab3792b4d2290c793b128a326" \
                         "c96234ac662793821063d887044e49f1014104f6e8c8581ee3dba51288e68386475fba780710c964" \
                         "dfb1aaabea06afb4fb0cd10282adf8bfed9fb94d959a089fcd19f691a0cc7b14b1f5aae5e132b39c" \
                         "c63efaffffffff0280d87407030000001976a914f5118746a4dce6ac146077f73fea49e10b1e908e" \
                         "88ac401c59c0020000001976a914c2a7a8f990252e6e048476b6a7a4433be10e9c3588ac00000000"

        pybtcd_deserialized_transaction = deserialize(rawtransaction)
        bitcoind_json_vout0 =  {"value" : 130.10000000,
                                     "n" : 0,
                                     "scriptPubKey" : {
                                         "asm" : "OP_DUP OP_HASH160 f5118746a4dce6ac146077f73fea49e10b1e908e OP_EQUALVERIFY OP_CHECKSIG",
                                         "hex" : "76a914f5118746a4dce6ac146077f73fea49e10b1e908e88ac",
                                         "reqSigs" : 1,
                                         "type" : "pubkeyhash",
                                         "addresses" : [
                                             "1PLoYttF6YdytJRzdnyubpEethhn5B8836"
                                         ]}
                                     }

        sut = VOUTDecoder.decode(pybtcd_deserialized_transaction['outs'][0], 0)
        vout = json.loads(json.dumps(bitcoind_json_vout0), parse_float=Decimal)
        self.assertEqual(vout, sut)

    def test__decode_PayToPubKey_65_bytes(self):
        rawtransaction = "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff0704f" \
                         "fff001d0104ffffffff0100f2052a0100000043410496b538e853519c726a2c91e61ec11600ae1390813a62" \
                         "7c66fb8be7947be63c52da7589379515d4e0a604f8141781e62294721166bf621e73a82cbf2342c858eeac0" \
                         "0000000"
        pybtcd_deserialized_transaction = deserialize(rawtransaction)
        bitcoind_json_vout0 = {"value" : 50.00000000,
                               "n" : 0,
                               "scriptPubKey" : {
                                   "asm" : "0496b538e853519c726a2c91e61ec11600ae1390813a627c66fb8be7947be63c52da7589379515d4e0a604f8141781e62294721166bf621e73a82cbf2342c858ee OP_CHECKSIG",
                                   "hex" : "410496b538e853519c726a2c91e61ec11600ae1390813a627c66fb8be7947be63c52da7589379515d4e0a604f8141781e62294721166bf621e73a82cbf2342c858eeac",
                                   "reqSigs" : 1,
                                   "type" : "pubkey",
                                   "addresses" : [
                                       "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX"
                                   ]
                               }
                           }
        sut = VOUTDecoder.decode(pybtcd_deserialized_transaction['outs'][0], 0)
        vout = json.loads(json.dumps(bitcoind_json_vout0), parse_float=Decimal)
        self.assertEqual(vout, sut)

    def test__decode_PayToPubKey_33_bytes(self):
        rawtransaction = "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff3c049" \
                         "93c1c4f02b0002c4d4d3d3d7df37de04d7764c9945027b3d19e66a03ef56bdd230f36648ad8b4b0ce9e2a81" \
                         "0100000000000000062f503253482fffffffff0100f2052a010000002321024d57123256b2a84e6618bc12b" \
                         "08f81cd54ec79fcd7a55a129eee9402bac8d5f7ac00000000"
        pybtcd_deserialized_transaction = deserialize(rawtransaction)
        bitcoind_json_vout0 = {"value" : 50.00000000,
                               "n" : 0,
                               "scriptPubKey" : {
                                   "asm" : "024d57123256b2a84e6618bc12b08f81cd54ec79fcd7a55a129eee9402bac8d5f7 OP_CHECKSIG",
                                   "hex" : "21024d57123256b2a84e6618bc12b08f81cd54ec79fcd7a55a129eee9402bac8d5f7ac",
                                   "reqSigs" : 1,
                                   "type" : "pubkey",
                                   "addresses" : [
                                       "1PLDXZPhFEfGGxdXr54FxvWUvWcRCrjHEG"
                                   ]
                               }
                           }
        sut = VOUTDecoder.decode(pybtcd_deserialized_transaction['outs'][0], 0)
        vout = json.loads(json.dumps(bitcoind_json_vout0), parse_float=Decimal)
        self.assertEqual(vout, sut)


    def test__decode_OPRETURN(self):
        rawtransaction = "0100000001c858ba5f607d762fe5be1dfe97ddc121827895c2562c4348d69d02b91dbb408e0100000" \
                         "08b4830450220446df4e6b875af246800c8c976de7cd6d7d95016c4a8f7bcdbba81679cbda2420221" \
                         "00c1ccfacfeb5e83087894aa8d9e37b11f5c054a75d030d5bfd94d17c5bc953d4a0141045901f6367" \
                         "ea950a5665335065342b952c5d5d60607b3cdc6c69a03df1a6b915aa02eb5e07095a2548a98dcdd84" \
                         "d875c6a3e130bafadfd45e694a3474e71405a4ffffffff020000000000000000156a13636861726c6" \
                         "579206c6f766573206865696469400d0300000000001976a914b8268ce4d481413c4e848ff353cd16" \
                         "104291c45b88ac00000000"

        pybtcd_deserialized_transaction = deserialize(rawtransaction)
        bitcoind_json_vout0 = {"value" : 0.00000000,
                                    "n" : 0,
                                    "scriptPubKey" : {
                                        "asm" : "OP_RETURN 636861726c6579206c6f766573206865696469",
                                        "hex" : "6a13636861726c6579206c6f766573206865696469",
                                        "type" : "nulldata"
                                    }
                                }
        sut = VOUTDecoder.decode(pybtcd_deserialized_transaction['outs'][0], 0)
        vout = json.loads(json.dumps(bitcoind_json_vout0), parse_float=Decimal)
        self.assertEqual(vout, sut)

    def test__decode_P2SH(self):
        rawtransaction = "0100000001323fcde8eb922407811af73ace8a621587f0e3756d9daa0306f43e9ee806701401000000fc" \
                         "004730440220385b914def508fe2e19e4db04eb3a242f9f2052ca4850e4d4ef47086c2ff0ca20220323c" \
                         "67b383d34731c3adcc231b3efbbd385a1ac1f9edbb03794361b0f8c39775014730440220663eb7920041" \
                         "7e448da1acfbf16543045ff42a8e2c64121589062f0e5311e879022010cb0965a9aa96bab8824778c2ae" \
                         "790ec14ed3bfaf4905478021152cbf78517f014c69522102d125ff449e4de303919ef232dafa0bc7528b" \
                         "266a576da91f6fd25a4709f98337210290418ccfa7e5ca60c01d5525be826dc791009e698519b4c090b4" \
                         "5e75ec8887d4210329ff00450d9756ecc26fc5446aebce88d4053f30cb08768e7cce3d172983d58f53ae" \
                         "ffffffff020b7e32000000000017a9146af7caf9b09224af8a171318f69d254c1756e54e87db8f0f2c00" \
                         "00000017a914fe9840ab09de0fa3d2f4c73da1d1fc49f0c0bb508700000000"

        pybtcd_deserialized_transaction = deserialize(rawtransaction)
        bitcoind_json_vout0 = {"value" : 0.03309067,
                                    "n" : 0,
                                    "scriptPubKey" : {
                                        "asm" : "OP_HASH160 6af7caf9b09224af8a171318f69d254c1756e54e OP_EQUAL",
                                        "hex" : "a9146af7caf9b09224af8a171318f69d254c1756e54e87",
                                        "reqSigs" : 1,
                                        "type" : "scripthash",
                                        "addresses" : [
                                            "3BScPpzxa8LErVDWg7zfHC5wcGHQf8F5pi"
                                        ]
                                    }
                                }
        sut = VOUTDecoder.decode(pybtcd_deserialized_transaction['outs'][0], 0)
        vout = json.loads(json.dumps(bitcoind_json_vout0), parse_float=Decimal)
        self.assertEqual(vout, sut)

    def test__decode_OPINT(self):
        pass