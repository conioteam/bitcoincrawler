from time import sleep
from unittest import TestCase
from subprocess import call
import random
from bitcoincrawler.bitcoind_backend import BitcoindBackend

__author__ = 'mirko'

class TestBitcoindBackend(TestCase):
    wait = False

    def setUp(self):
        port_number = 11235
        #Command line client:
        # bitcoin-cli -regtest=1 -rpcport=11235 -rpcuser=test_bitcoincrawler -rpcpassword=test_bitcoincrawler_pwd -testnet=0

        call(['bitcoind',
              '-rpcuser=test_bitcoincrawler',
              '-rpcpassword=test_bitcoincrawler_pwd',
              '-datadir=bitcoincrawler/test/bitcoind_data',
              '-regtest',
              '-pid=bitcoind_data/bitcoincrawler.pid',
              '-rpcport={}'.format(port_number),
              '--daemon',
              '-listen=0'])
        self.sut = BitcoindBackend('test_bitcoincrawler', 'test_bitcoincrawler_pwd', 'http://127.0.0.1:{}'.format(port_number))
        if self.wait:
            sleep(5)
            self.wait = False

    def tearDown(self):
        # For unclear reasons, bitcoind does not produce bitcoind.pid, which is necessary
        # to tear it down
        pass

    def test_get_missing_blocks_num(self):
        missing_blocks = self.sut.get_missing_blocks(100, 10)
        self.assertEquals(120 - 100 + 10, len(list(missing_blocks)))

    def test_get_missing_blocks(self):
        missing_blocks = list(self.sut.get_missing_blocks(100, 10))
        hash_0 = missing_blocks[0]['hash']
        hash_last = missing_blocks[-1]['hash']

        self.assertEqual('00f3236523fad4de8254cff71f1df0cf1a06fa5f630b8396abfeff076192b9e7', hash_0)
        self.assertEqual('1c659ee59c4d4ef6147b064dcfc6600cadcedb8cfa9f14a7c265f54ec6b67740', hash_last)

    def test_get_block(self):
        block = self.sut._get_block(block_num=10)
        self.assertEquals('48310552612a11861a895639a1f58549b288739a2a8b0bc4a33ccfb35d2ef25d',
                          block['hash'])

        block = self.sut._get_block(block_hash='48310552612a11861a895639a1f58549b288739a2a8b0bc4a33ccfb35d2ef25d')
        self.assertEquals('48310552612a11861a895639a1f58549b288739a2a8b0bc4a33ccfb35d2ef25d',
                          block['hash'])

    def test_get_mempool_txs(self):
        txs = list(self.sut.get_mempool_txs())

        self.assertEqual(4, len(txs))

        self.assertEqual(
            'fc333fd09f5dac7eb6ed5d246a21733299fc32f1646305ad7dabf8eed3788914',
            txs[0]['txid']
        )

        self.assertEqual(
            '63c5ce1846a40dc7a2a78a139baaf7c631103d201fc9e3c8144e2516f11c9cc2',
            txs[1]['txid']
        )

        self.assertEqual(
            '332d78d265ceba2c2f77a8bc6fa98fdcb29c7394298b6a52ac5eee045f452add',
            txs[2]['txid']
        )

        self.assertEqual(
            '58fe68544719d2f360bb9b298af99fc29dbe73fb5b880dd7b332daef95914fe7',
            txs[3]['txid']
        )

    def test_get_transactions_from_block(self):
        txs = list(self.sut.get_transactions_from_block(
            {
                'tx': [
                    '20c45d1af3a8982b6f2e0af86a49357e478ff06eef9d793842ea6e39043edd81',
                    '4832b962ae67b0e006588d8c2097f813eae9cfa871d0bea2491b9b656ce9b077'
                ]
            }
        ))

        self.assertEqual(2, len(txs))

        self.assertEqual('20c45d1af3a8982b6f2e0af86a49357e478ff06eef9d793842ea6e39043edd81', txs[0]['txid'])
        self.assertEqual('4832b962ae67b0e006588d8c2097f813eae9cfa871d0bea2491b9b656ce9b077', txs[1]['txid'])

    def test_get_inputs_from_transaction(self):
        inputs = self.sut.get_inputs_from_transaction(
            {
                "txid" : "24e0ba1b7578fe6f0434ccd3f897023b8b1963ac8c1862d3063277b5b4820ce0",
                "version" : 1,
                "locktime" : 0,
                "vin" : [
                    {
                        "coinbase" : "5a0101",
                        "sequence" : 4294967295
                    }
                ],
                "vout" : [
                    {
                        "value" : 50.00000000,
                        "n" : 0,
                        "scriptPubKey" : {
                            "asm" : "0345b97574eac06064a7014e03d6287b7e881588635587bc6ed5edcabf962b8623 OP_CHECKSIG",
                            "hex" : "210345b97574eac06064a7014e03d6287b7e881588635587bc6ed5edcabf962b8623ac",
                            "reqSigs" : 1,
                            "type" : "pubkey",
                            "addresses" : [
                                "mmWraAGKp6z2wnRbnPaJZjSWiYoPdwCpYo"
                            ]
                        }
                    }
                ]
            }
        )

        inputs = list(inputs)

        self.assertEqual(1, len(inputs))
        self.assertEqual("5a0101", inputs[0]['coinbase'])

    def test_get_outputs_from_transaction(self):
        outputs = self.sut.get_outputs_from_transaction(
            {
                "txid" : "24e0ba1b7578fe6f0434ccd3f897023b8b1963ac8c1862d3063277b5b4820ce0",
                "version" : 1,
                "locktime" : 0,
                "vin" : [
                    {
                        "coinbase" : "5a0101",
                        "sequence" : 4294967295
                    }
                ],
                "vout" : [
                    {
                        "value" : 50.00000000,
                        "n" : 0,
                        "scriptPubKey" : {
                            "asm" : "0345b97574eac06064a7014e03d6287b7e881588635587bc6ed5edcabf962b8623 OP_CHECKSIG",
                            "hex" : "210345b97574eac06064a7014e03d6287b7e881588635587bc6ed5edcabf962b8623ac",
                            "reqSigs" : 1,
                            "type" : "pubkey",
                            "addresses" : [
                                "mmWraAGKp6z2wnRbnPaJZjSWiYoPdwCpYo"
                            ]
                        }
                    }
                ]
            }
        )

        outputs = list(outputs)

        self.assertEqual(1, len(outputs))
        self.assertEqual("210345b97574eac06064a7014e03d6287b7e881588635587bc6ed5edcabf962b8623ac",
                         outputs[0]['scriptPubKey']['hex'])
