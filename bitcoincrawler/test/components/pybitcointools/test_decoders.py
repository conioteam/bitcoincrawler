from unittest import TestCase
from bitcoincrawler.components.pybitcointools.decoders import VINDecoder, VOUTDecoder
from bitcoin import deserialize
import json
from decimal import Decimal

class TestVINDecoder(TestCase):
    def test_Vin(self):
        rawtransaction = "01000000031091bb34c19754b689685bd5f84078b437653d08377d2d03d256b34f80eb219e010000008a4730440" \
                         "220476c26cdcecccf46fdd96fb87814661cb1044e103d1bcd5be339b9cbaceca47902201b2caafe5b36913ef475" \
                         "d4d33b9d62aa3316ece6f1ac3371a506906e61afd4510141048c632401521a105db6b62db0a2c393181b5538f2c" \
                         "56d461057611252baebc9c7794378c252c45b7393fc93ea3b8bc6d6db1c9b5506744d51d1ddd7a9acd27d81ffff" \
                         "ffffcc72f7a8acf77c1b1313d4ba229bff7db4f40e0a1b525a9b8a4dbc8ecc80b070000000008b4830450221009" \
                         "97b74ef85d3be61a96a4d8ecebfeb588979364276f54fa77571ff8fb7906e4202204390f9935695194362fbc221" \
                         "b00436b4811d01f645715105f9d081ad65977e2b014104fd579aa4983cece29365038ddbaf479af86bdf25afdca" \
                         "e67bbe8b30c268aecdac6cd8f923ef3f23ab694783f9243522f67886a46a43499e3fb3ed49623869d6fffffffff" \
                         "8ecdae566b8e8d709a32054175ce61fc2a9323e60023f62b23c342a7186beeea000000008b48304502200f95d4c" \
                         "d51bb5b867563700979ea23bf69921b1a0262ff5de3d7330bb992a713022100de58fa5822e7e62c8e6e4edbdece" \
                         "7913cb21f5a7b5a39d85fa9291874ce81a710141045f7f6eed56863bf527b8fd30cbe78038db311370da6c7054b" \
                         "eced527d60f47a65d6f1ce62278ba496f5da4a3d738eac0e2cb0f4ac38b113cbeabef59b685b16cffffffff0280" \
                         "c51b11010000000576a90088ac4cbdd397a90000001976a914d1121a58483d135c953e0f4e2cc6d126b5c6b0638" \
                         "8ac00000000"
        pybtcd_deserialized_transaction = deserialize(rawtransaction)
        bitcoind_json_vin0 = {"txid" : "9e21eb804fb356d2032d7d37083d6537b47840f8d55b6889b65497c134bb9110",
                              "vout" : 1,
                              "scriptSig" : {
                                  "asm" : "30440220476c26cdcecccf46fdd96fb87814661cb1044e103d1bcd5be339b9cbaceca47902201b2caafe5b36913ef475d4d33b9d62aa3316ece6f1ac3371a506906e61afd45101 048c632401521a105db6b62db0a2c393181b5538f2c56d461057611252baebc9c7794378c252c45b7393fc93ea3b8bc6d6db1c9b5506744d51d1ddd7a9acd27d81",
                                  "hex" : "4730440220476c26cdcecccf46fdd96fb87814661cb1044e103d1bcd5be339b9cbaceca47902201b2caafe5b36913ef475d4d33b9d62aa3316ece6f1ac3371a506906e61afd4510141048c632401521a105db6b62db0a2c393181b5538f2c56d461057611252baebc9c7794378c252c45b7393fc93ea3b8bc6d6db1c9b5506744d51d1ddd7a9acd27d81"
                              },
                              "sequence" : 4294967295
                          }
        sut = VINDecoder.decode(pybtcd_deserialized_transaction['ins'][0])
        vin = json.loads(json.dumps(bitcoind_json_vin0), parse_float=Decimal)

        self.assertEqual(vin, sut)

    def test_Vin_coinbase(self):
        rawtransaction = "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff320" \
                         "380a305254b6e434d696e6572422d50322f4256383030303030302fbf2cf98be334867355cb0d80087e7f" \
                         "04000049e12b00ffffffff02fcde0600000000001976a9148c1fe3d123c397d6ed6b53e82069c0d68cabe" \
                         "cb588ac0c492e95000000001976a914396652927daedcef95e1fb89a09faf09545c322588ac00000000"
        pybtcd_deserialized_transaction = deserialize(rawtransaction)
        bitcoind_json_vin0 = {
            "coinbase" : "0380a305254b6e434d696e6572422d50322f4256383030303030302fbf2cf98be334867355cb0d80087e7f04000049e12b00",
            "sequence" : 4294967295
        }
        sut = VINDecoder.decode(pybtcd_deserialized_transaction['ins'][0])
        vin = json.loads(json.dumps(bitcoind_json_vin0), parse_float=Decimal)
        self.assertEqual(vin, sut)

class TestVOUTDecoder(TestCase):
    def test__decode_PayToPubKeyHash(self):
        """
        OP_DUP OP_HASH160 OP_DATA_20 OP_EQUALVERIFY OP_CHECKSIG
        """
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

        sut = VOUTDecoder.decode(pybtcd_deserialized_transaction['outs'][0], 0, "main")
        vout = json.loads(json.dumps(bitcoind_json_vout0), parse_float=Decimal)
        self.assertEqual(vout, sut)

    def test__decode_PayToPubKey_65_bytes(self):
        """
        OP_DATA_65 OP_CHECKSIG
        """
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
        sut = VOUTDecoder.decode(pybtcd_deserialized_transaction['outs'][0], 0, "main")
        vout = json.loads(json.dumps(bitcoind_json_vout0), parse_float=Decimal)
        self.assertEqual(vout, sut)

    def test__decode_PayToPubKey_33_bytes(self):
        """
        OP_DATA_33 OP_CHECKSIG
        """
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
        sut = VOUTDecoder.decode(pybtcd_deserialized_transaction['outs'][0], 0, "main")
        vout = json.loads(json.dumps(bitcoind_json_vout0), parse_float=Decimal)
        self.assertEqual(vout, sut)


    def test__decode_OPRETURN_data(self):
        """
        OP_RETURN OP_DATA
        """
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
        sut = VOUTDecoder.decode(pybtcd_deserialized_transaction['outs'][0], 0, "main")
        vout = json.loads(json.dumps(bitcoind_json_vout0), parse_float=Decimal)
        self.assertEqual(vout, sut)

    def test__decode_OPRETURN(self):
        pass

    def test__decode_P2SH(self):
        """
        OP_HASH160 OP_DATA_20 OP_EQUAL
        """
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
        sut = VOUTDecoder.decode(pybtcd_deserialized_transaction['outs'][0], 0, "main")
        vout = json.loads(json.dumps(bitcoind_json_vout0), parse_float=Decimal)
        self.assertEqual(vout, sut)

    def test__decode_CHECKMULTISIG_1_of_3(self):
        """
        OP1~21 OP_DATA(65 or 33bytes)*N OP_N OP_CHECKMULTISIG
        :return:
        """
        rawtransaction = "010000000337bd40a022eea1edd40a678cddabe200b131afd5797b232ac21861d8e97eb367020000008a4" \
                         "730440220e8343f8ac7e96582d92a450ce314668db4f7a0e2c94a97aa6df026f93ebee2290220866b5728" \
                         "d4247688d91b4a30144762bc8bfd7f385de7f7d326d665ff5e3e900301410461cbdcc5409fb4b4d42b51d" \
                         "33381354d80e550078cb532a34bfa2fcfdeb7d76519aecc62770f5b0e4ef8551946d8a540911abe3e7854" \
                         "a26f39f58b25c15342afffffffff96420befb14a9357181e5da089824a3e6ea5a95856ff74c06c7d5ea98" \
                         "d633cf9020000008a4730440220b7227a8f816f3810f97057102edf8be4434c1e00f48b4440976bcc478f" \
                         "1431030220af3cba150afdd44618de4369cdc65fea73e447d7b5fbe135d2f08f86d82aa85f01410461cbd" \
                         "cc5409fb4b4d42b51d33381354d80e550078cb532a34bfa2fcfdeb7d76519aecc62770f5b0e4ef8551946" \
                         "d8a540911abe3e7854a26f39f58b25c15342afffffffff96420befb14a9357181e5da089824a3e6ea5a95" \
                         "856ff74c06c7d5ea98d633cf9010000008a47304402207d689e1a61e06440eab18d961517a97c49219a91" \
                         "f2c59d9630e902fcb2f4ea8b0220dcd274349ca264d8bd2bee5135664a92899e94a319a349d6d6e3660d0" \
                         "4b564ad0141047a4c5d104002ebc203bef5cab6f13ff57ab624bb5f9f1186beb64c83a396da0d912e11a1" \
                         "8ea15a2c784a62fed2bbd8258c3413c18bf4c3f2ba28f3d5565e328bffffffff0340420f0000000000875" \
                         "14104cc71eb30d653c0c3163990c47b976f3fb3f37cccdcbedb169a1dfef58bbfbfaff7d8a473e7e2e6d3" \
                         "17b87bafe8bde97e3cf8f065dec022b51d11fcdd0d348ac4410461cbdcc5409fb4b4d42b51d33381354d8" \
                         "0e550078cb532a34bfa2fcfdeb7d76519aecc62770f5b0e4ef8551946d8a540911abe3e7854a26f39f58b" \
                         "25c15342af52ae50cec402000000001976a914c812a297b8e0e778d7a22bb2cd6d23c3e789472b88ac20a" \
                         "10700000000001976a914641ad5051edd97029a003fe9efb29359fcee409d88ac00000000"
        pybtcd_deserialized_transaction = deserialize(rawtransaction)
        bitcoind_json_vout0 = {"value" : 0.01000000,
                               "n" : 0,
                               "scriptPubKey" : {
                                   "asm" : "1 04cc71eb30d653c0c3163990c47b976f3fb3f37cccdcbedb169a1dfef58bbfbfaff7d8a473e7e2e6d317b87bafe8bde97e3cf8f065dec022b51d11fcdd0d348ac4 0461cbdcc5409fb4b4d42b51d33381354d80e550078cb532a34bfa2fcfdeb7d76519aecc62770f5b0e4ef8551946d8a540911abe3e7854a26f39f58b25c15342af 2 OP_CHECKMULTISIG",
                                   "hex" : "514104cc71eb30d653c0c3163990c47b976f3fb3f37cccdcbedb169a1dfef58bbfbfaff7d8a473e7e2e6d317b87bafe8bde97e3cf8f065dec022b51d11fcdd0d348ac4410461cbdcc5409fb4b4d42b51d33381354d80e550078cb532a34bfa2fcfdeb7d76519aecc62770f5b0e4ef8551946d8a540911abe3e7854a26f39f58b25c15342af52ae",
                                   "reqSigs" : 1,
                                   "type" : "multisig",
                                   "addresses" : [
                                       "1AJbsFZ64EpEfS5UAjAfcUG8pH8Jn3rn1F",
                                       "1A8JiWcwvpY7tAopUkSnGuEYHmzGYfZPiq"
                                   ]
                               }
                           }
        sut = VOUTDecoder.decode(pybtcd_deserialized_transaction['outs'][0], 0, "main")
        vout = json.loads(json.dumps(bitcoind_json_vout0), parse_float=Decimal)
        self.assertEqual(sut, vout)

    def test__decode_CHECKMULTISIG_1_of_2(self):
            rawtransaction = "010000000123ba84a7ce8ab2785a838fa9ca50ad395bee25aba38dda28336cc337d08a599e000000006a4730" \
                             "440220320a58bf09ce578dd2ddf5381a34d80c3b659e2748c8fd8aa1b7ecc5b8c87665022019905d76a7bbc8" \
                             "3cbc3fb6d33e7e8aae903716206e9cf1fcb75518ce37baf69a01210312c50bdc21e06827c0bdd3ef1ff849e2" \
                             "4b17147f9a6f240c4af45bd235eb5819ffffffff0102000000000000004751210351efb6e91a31221652105d" \
                             "032a2508275f374cea63939ad72f1b1e02f477da782100f2b7816db49d55d24df7bdffdbc1e203b424e8cd39" \
                             "f5651ab938e5e4a193569e52ae00000000"

            pybtcd_deserialized_transaction = deserialize(rawtransaction)
            bitcoind_json_vout0 = {"value" : 0.00000002,
                                   "n" : 0,
                                   "scriptPubKey" : {
                                       "asm" : "1 0351efb6e91a31221652105d032a2508275f374cea63939ad72f1b1e02f477da78 00f2b7816db49d55d24df7bdffdbc1e203b424e8cd39f5651ab938e5e4a193569e 2 OP_CHECKMULTISIG",
                                       "hex" : "51210351efb6e91a31221652105d032a2508275f374cea63939ad72f1b1e02f477da782100f2b7816db49d55d24df7bdffdbc1e203b424e8cd39f5651ab938e5e4a193569e52ae",
                                       "reqSigs" : 1,
                                       "type" : "multisig",
                                       "addresses" : [
                                           "1NdB761LmTmrJixxp93nz7pEiCx5cKPW44"
                                       ]
                                   }
                               }
            sut = VOUTDecoder.decode(pybtcd_deserialized_transaction['outs'][0], 0, "main")
            vout = json.loads(json.dumps(bitcoind_json_vout0), parse_float=Decimal)
            self.assertEqual(sut, vout)

    def test__decode_OPDATA_nonstandard(self):
        """
        OP_DATA_32
        OP_DATA_36
        """
        rawtransaction = "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff2cfabe6d" \
                         "6dc4a1165ea4f5b251a55d0a5826282b4a9b3551a28d9ff0d9343a1bc942fa895e0100000000000000ffffffff" \
                         "0e00000000000000002120b7837f89bd7d3b262037ed0e31063c00d8e5f785b742ac467cef4e69d98a19bd5f71" \
                         "2300000000001976a91404b61d237655b3ceb6329ac474cd4eb16fa7318f88accf057b00000000001976a9147f" \
                         "92bc474f4d80ac06c8f02d57915bf550c8447b88aca16f850100000000434104ffd03de44a6e11b9917f3a29f9" \
                         "443283d9871c9d743ef30d5eddcd37094b64d1b3d8090496b53256786bf5c82932ec23c3b74d9f05a6f95a8b55" \
                         "29352656664bacb17fe203000000001976a9149fdc63fd4c87de443b5984d00b159a8340f64eb388acd88f4d04" \
                         "000000001976a91491ce910c7ca125114f2e38bf9a17f1130185ca7f88ac2fae2d0b000000001976a91426bad6" \
                         "b6f1079452cd954471d58a641dcd20abb888ac6ee2f50e000000001976a914761331627d4769d4e551762caa58" \
                         "f54fb65822a188ace92add0f000000001976a914984f8de73e491543c52a7cb23537706887247f8688acb1fc8f" \
                         "1f000000001976a9147522e01f331ef160bf609ddc321033a87529ccb688ac02767426000000001976a914bcf8" \
                         "2a713a320942ce47e073787b48e73ed21bc388ac3333752d000000001976a914155b7de88446ba2fb671df7e3e" \
                         "68def8646e1cda88ac331f893f0000000043410461c9f86eb47bda456cedc2e4bc45a51026b244db1f3fd4c2d2" \
                         "5713f517062b6c832f2e9231eba78e92eb77ce122498d99cea3007bdba9bed715e4525b92e8cc9ac79dfb64200" \
                         "0000001976a914af1ffe62761b0c8b83d96f06621eda34b1b0683288ac00000000"
        pybtcd_deserialized_transaction = deserialize(rawtransaction)
        bitcoind_json_vout0 = {"value" : 0.00000000,
                               "n" : 0,
                               "scriptPubKey" : {
                                   "asm" : "b7837f89bd7d3b262037ed0e31063c00d8e5f785b742ac467cef4e69d98a19bd",
                                   "hex" : "20b7837f89bd7d3b262037ed0e31063c00d8e5f785b742ac467cef4e69d98a19bd",
                                   "type" : "nonstandard"
                               }
                           }
        sut = VOUTDecoder.decode(pybtcd_deserialized_transaction['outs'][0], 0, "main")
        vout = json.loads(json.dumps(bitcoind_json_vout0), parse_float=Decimal)
        self.assertEqual(sut, vout)

    def test__decode_nonstandard_transaction(self):
        rawtransaction = "01000000031091bb34c19754b689685bd5f84078b437653d08377d2d03d256b34f80eb219e010000008a473044" \
                         "0220476c26cdcecccf46fdd96fb87814661cb1044e103d1bcd5be339b9cbaceca47902201b2caafe5b36913ef4" \
                         "75d4d33b9d62aa3316ece6f1ac3371a506906e61afd4510141048c632401521a105db6b62db0a2c393181b5538" \
                         "f2c56d461057611252baebc9c7794378c252c45b7393fc93ea3b8bc6d6db1c9b5506744d51d1ddd7a9acd27d81" \
                         "ffffffffcc72f7a8acf77c1b1313d4ba229bff7db4f40e0a1b525a9b8a4dbc8ecc80b070000000008b48304502" \
                         "2100997b74ef85d3be61a96a4d8ecebfeb588979364276f54fa77571ff8fb7906e4202204390f9935695194362" \
                         "fbc221b00436b4811d01f645715105f9d081ad65977e2b014104fd579aa4983cece29365038ddbaf479af86bdf" \
                         "25afdcae67bbe8b30c268aecdac6cd8f923ef3f23ab694783f9243522f67886a46a43499e3fb3ed49623869d6f" \
                         "ffffffff8ecdae566b8e8d709a32054175ce61fc2a9323e60023f62b23c342a7186beeea000000008b48304502" \
                         "200f95d4cd51bb5b867563700979ea23bf69921b1a0262ff5de3d7330bb992a713022100de58fa5822e7e62c8e" \
                         "6e4edbdece7913cb21f5a7b5a39d85fa9291874ce81a710141045f7f6eed56863bf527b8fd30cbe78038db3113" \
                         "70da6c7054beced527d60f47a65d6f1ce62278ba496f5da4a3d738eac0e2cb0f4ac38b113cbeabef59b685b16c" \
                         "ffffffff0280c51b11010000000576a90088ac4cbdd397a90000001976a914d1121a58483d135c953e0f4e2cc6" \
                         "d126b5c6b06388ac00000000"
        pybtcd_deserialized_transaction = deserialize(rawtransaction)
        bitcoind_json_vout0 = {"value" : 45.82000000,
                                "n" : 0,
                                "scriptPubKey" : {
                                    "asm" : "OP_DUP OP_HASH160 0 OP_EQUALVERIFY OP_CHECKSIG",
                                    "hex" : "76a90088ac",
                                    "type" : "nonstandard"
                                }
                            }
        sut = VOUTDecoder.decode(pybtcd_deserialized_transaction['outs'][0], 0, "main")
        vout = json.loads(json.dumps(bitcoind_json_vout0), parse_float=Decimal)
        self.assertEqual(sut, vout)

    def test_decode_nonstandard_transaction_1(self):
        """
        txid: e411dbebd2f7d64dafeef9b14b5c59ec60c36779d43f850e5e347abee1e1a455
        """
        rawtransaction = "010000000127d57276f1026a95b4af3b03b6aba859a001861682342af19825e8a2408ae008010000008c49304" \
                         "6022100cd92b992d4bde3b44471677081c5ece6735d6936480ff74659ac1824d8a1958e022100b08839f16753" \
                         "2aea10acecc9d5f7044ddd9793ef2989d090127a6e626dc7c9ce014104cac6999d6c3feaba7cdd6c62bce1743" \
                         "39190435cffd15af7cb70c33b82027deba06e6d5441eb401c0f8f92d4ffe6038d283d2b2dd59c4384b66b7b8f" \
                         "038a7cf5ffffffff0200093d0000000000434104636d69f81d685f6f58054e17ac34d16db869bba8b3562aabc" \
                         "38c35b065158d360f087ef7bd8b0bcbd1be9a846a8ed339bf0131cdb354074244b0a9736beeb2b9ac40420f00" \
                         "00000000fdba0f76a9144838a081d73cf134e8ff9cfd4015406c73beceb388"+ ("ac"*4002) + "00000000"
        pybtcd_deserialized_transaction = deserialize(rawtransaction)
        bitcoind_json_vout0 = {
                                   "value" : 0.01000000,
                                   "n" : 1,
                                   "scriptPubKey" : {
                                       "asm" : "OP_DUP OP_HASH160 4838a081d73cf134e8ff9cfd4015406c73beceb3 OP_EQUALVERIFY" + (" OP_CHECKSIG"*4002),
                                       "hex" : "76a9144838a081d73cf134e8ff9cfd4015406c73beceb388" + ("ac"*4002),
                                       "type" : "nonstandard"
                                   }
                               }
        sut = VOUTDecoder.decode(pybtcd_deserialized_transaction['outs'][1], 1, "main")
        vout = json.loads(json.dumps(bitcoind_json_vout0), parse_float=Decimal)
        self.assertEqual(sut, vout)

    def test_decode_nonstandard_transaction_2(self):
        """
        5492a05f1edfbd29c525a3dbf45f654d0fc45a805ccd620d0a4dff47de63f90b
        :return:
        """
        rawtransaction = "0100000001d488bf79a92feb869c984de9fc6be7cb5c5ac2e408d608e25460501c2aff2dac010000008a47304402200f" \
                         "185ac16694f3f3902fb058f1a3d96f2549db4311b038742fc315685c9e6a1f022018e6c2c8e0559d87988b48ba80d214" \
                         "d95ed3f06795e549d4568702cc2a9e2af301410463cd01a8f2b56fff4e9357ccedf014ca119d64c1dff8b576e2785f60" \
                         "3b3fd1a04e7ab451929ef5e4e2449a7999a1365db7bc08fccc19cdad16c4ce26d6ba9bf4ffffffff03008aa411000000" \
                         "001a76a91469d28eb9a311256338d281025a7437096149472c88ac610065cd1d000000001976a9145f8b65a4064ef5c0" \
                         "71c382d594b55d94bd31ec3a88ac00100000000000001976a9146300bf4c5c2a724c280b893807afb976ec78a92b88ac" \
                         "00000000"
        pybtcd_deserialized_transaction = deserialize(rawtransaction)
        bitcoind_json_vout0 = {
                "value" : 2.95995904,
                "n" : 0,
                "scriptPubKey" : {
                    "asm" : "OP_DUP OP_HASH160 69d28eb9a311256338d281025a7437096149472c OP_EQUALVERIFY OP_CHECKSIG OP_NOP",
                    "hex" : "76a91469d28eb9a311256338d281025a7437096149472c88ac61",
                    "type" : "nonstandard"
                }
        }
        sut = VOUTDecoder.decode(pybtcd_deserialized_transaction['outs'][0], 0, "main")
        vout = json.loads(json.dumps(bitcoind_json_vout0), parse_float=Decimal)
        self.assertEqual(sut, vout)


    def test_decode_nonstandard_transaction_3(self):
        """
        b728387a3cf1dfcff1eef13706816327907f79f9366a7098ee48fc0c00ad2726
        :return:
        """
        rawtransaction = "0100000001658d363400dac6f939da9065c853a77d07d7e62e60a3bb8c1063437fc0018cff000000008b483045022100" \
                         "e84437d13d6f316ee69e3328c77dba344a0da973fb40b4974a753e65cf8fae0c02205f3de940ad995e3f960523e9afa5" \
                         "f5cec71ed91ef16cb3dbd7a69a43fb8898a6014104e4411b8275776b110b3b06a7ac0d5927f08f95a476a97ab091436f" \
                         "e423de660fb9606ab64749ea360b7d624c9698d26d9965732017acd3da7e9ffc13daca0f26ffffffff02ee4d8a050000" \
                         "000043410467b7944809e4b3748d2cac0c388dad7ee3555b408a7892a8bf929e856afa2da4d329a39cf2c28f85438ae8" \
                         "d98a4d0bfb107b914933168eb9b31fae845fe8f614ac01000000000000004240f816b480f87144ec4de5862adf028ff6" \
                         "6cc6964250325d53fd22bf8922824b6f1e1f2c881ae0608ec77ebf88a75c66d3099113a7343238f2f7a0ebb91a4ed335" \
                         "ac00000000"
        pybtcd_deserialized_transaction = deserialize(rawtransaction)
        bitcoind_json_vout1 = {
            "value" : 0.00000001,
            "n" : 1,
            "scriptPubKey" : {
                "asm" : "f816b480f87144ec4de5862adf028ff66cc6964250325d53fd22bf8922824b6f1e1f2c881ae0608ec77ebf88a75c66d3099113a7343238f2f7a0ebb91a4ed335 OP_CHECKSIG",
                "hex" : "40f816b480f87144ec4de5862adf028ff66cc6964250325d53fd22bf8922824b6f1e1f2c881ae0608ec77ebf88a75c66d3099113a7343238f2f7a0ebb91a4ed335ac",
                "type" : "pubkey"
            }
        }
        sut = VOUTDecoder.decode(pybtcd_deserialized_transaction['outs'][1], 1, "main")
        vout = json.loads(json.dumps(bitcoind_json_vout1), parse_float=Decimal)
        self.assertEqual(sut, vout)

    def test_decode_nonstandard_transaction_4(self):
        """
        b728387a3cf1dfcff1eef13706816327907f79f9366a7098ee48fc0c00ad2726
        """
        rawtransaction = "0100000001658d363400dac6f939da9065c853a77d07d7e62e60a3bb8c1063437fc0018cff000000008b483045" \
                         "022100e84437d13d6f316ee69e3328c77dba344a0da973fb40b4974a753e65cf8fae0c02205f3de940ad995e3f" \
                         "960523e9afa5f5cec71ed91ef16cb3dbd7a69a43fb8898a6014104e4411b8275776b110b3b06a7ac0d5927f08f" \
                         "95a476a97ab091436fe423de660fb9606ab64749ea360b7d624c9698d26d9965732017acd3da7e9ffc13daca0f" \
                         "26ffffffff02ee4d8a050000000043410467b7944809e4b3748d2cac0c388dad7ee3555b408a7892a8bf929e85" \
                         "6afa2da4d329a39cf2c28f85438ae8d98a4d0bfb107b914933168eb9b31fae845fe8f614ac0100000000000000" \
                         "4240f816b480f87144ec4de5862adf028ff66cc6964250325d53fd22bf8922824b6f1e1f2c881ae0608ec77ebf" \
                         "88a75c66d3099113a7343238f2f7a0ebb91a4ed335ac00000000"
        pybtcd_deserialized_transaction = deserialize(rawtransaction)
        bitcoind_json_vout1 = {
            "value" : 0.00000001,
            "n" : 1,
            "scriptPubKey" : {
                "asm" : "f816b480f87144ec4de5862adf028ff66cc6964250325d53fd22bf8922824b6f1e1f2c881ae0608ec77ebf88a75c66d3099113a7343238f2f7a0ebb91a4ed335 OP_CHECKSIG",
                "hex" : "40f816b480f87144ec4de5862adf028ff66cc6964250325d53fd22bf8922824b6f1e1f2c881ae0608ec77ebf88a75c66d3099113a7343238f2f7a0ebb91a4ed335ac",
                "type" : "pubkey"
            }
        }
        sut = VOUTDecoder.decode(pybtcd_deserialized_transaction['outs'][1], 1, "main")
        vout = json.loads(json.dumps(bitcoind_json_vout1), parse_float=Decimal)
        self.assertEqual(sut, vout)