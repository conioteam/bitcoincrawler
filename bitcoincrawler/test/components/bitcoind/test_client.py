from unittest import TestCase
from requests.exceptions import ConnectionError
from bitcoincrawler.components.bitcoind.client import BitcoinCli
from bitcoincrawler.components.bitcoind.exceptions.client import BitcoinCliException, TransactionNotFound, BlockNotFound
import httpretty
from httpretty import httprettified
import json
from decimal import Decimal


class TestBitcoinCliAsync(TestCase):
    def setUp(self):
        self.sut = BitcoinCli('username', 'password', 'http://bitcoin_url/', async=False)
        self.async_auth_string = u'Basic dXNlcm5hbWU6cGFzc3dvcmQ='

    def test_auth_headers(self):
        self.assertEqual(self.sut.btcd_auth_header_async, self.async_auth_string)


class TestBitcoinCli(TestCase):
    def register_call(self, response):
        if isinstance(response, dict) or isinstance(response, list):
            response = json.dumps(response)
        return httpretty.register_uri(method=httpretty.POST,
                                      uri='http://bitcoin_url/',
                                      body=response)
    
    def setUp(self):
        self.sut = BitcoinCli('username', 'password', 'http://bitcoin_url/', async=False)
        self.auth_string = b'Basic dXNlcm5hbWU6cGFzc3dvcmQ='

    def test_auth_headers(self):
        self.assertEqual(self.sut.btcd_auth_header, self.auth_string)

    @httprettified
    def test_call_unexpected_response(self):
        self.register_call('Unexpected response')
        with self.assertRaises(BitcoinCliException) as raised:
            self.sut.call('method', 'param')
        e = raised.exception
        self.assertIsInstance(e.msg, ValueError)
        self.assertEqual(e.method, 'method')
        self.assertEqual(e.params[0], 'param')

    @httprettified
    def test_call_response_has_error(self):
        self.register_call({'error': 'some error message'})
        with self.assertRaises(BitcoinCliException):
            self.sut.call('method', 'param')

    @httprettified
    def test_call_successful_response(self):
        response = {'result': 'a successful result'}
        self.register_call(response)
        result = self.sut.call('method', 'param')
        self.assertEqual(result, response)

    @httprettified
    def test_call_bitcoind_is_gone(self):
        def response(r, u, h):
            raise ConnectionError('Connection aborted.', '', '')
        self.register_call(response)
        with self.assertRaises(BitcoinCliException):
            self.sut.call('method', 'param')

    @httprettified
    def test_get_raw_transaction_unknown_tx(self):
        response = {'error':{'message': 'No information available about transaction', 'code': -5}}
        self.register_call(response)
        with self.assertRaises(TransactionNotFound) as assertion:
            self.sut.get_raw_transaction('unknown_but_valid_txid')
        exception = assertion.exception
        self.assertEqual(exception.params, 'unknown_but_valid_txid')
        self.assertEqual(exception.method, 'getrawtransaction')
        payload = json.loads(httpretty.last_request().body.decode('utf-8'))
        self.assertEqual(payload.get('method'), 'getrawtransaction')
        self.assertEqual(payload.get('params')[0], 'unknown_but_valid_txid')

    @httprettified
    def test_get_raw_transaction_invalid_tx(self):
        response = {'error':{"code":-8, "message":"parameter 1 must be hexadecimal string (not 'invalid_txid')"}}
        self.register_call(response)
        with self.assertRaises(BitcoinCliException):
            self.sut.get_raw_transaction('invalid_txid')
        payload = json.loads(httpretty.last_request().body.decode('utf-8'))
        self.assertEqual(payload.get('method'), 'getrawtransaction')
        self.assertEqual(payload.get('params')[0], 'invalid_txid')

    @httprettified
    def test_get_raw_transaction(self):
        response = {"result": "valuid_rawtx"}
        self.register_call(response)
        r = self.sut.get_raw_transaction('valid_txid')
        self.assertEqual(r, response)
        payload = json.loads(httpretty.last_request().body.decode('utf-8'))
        self.assertEqual(payload.get('method'), 'getrawtransaction')
        self.assertEqual(payload.get('params')[0], 'valid_txid')

    @httprettified
    def test_decode_raw_transaction_success(self):
        response = {"result": {
                    "txid": "86abfcb417f4be40ea74fc1b3719bea79502e8178aafb3aa144ffc9175f6f132",
                    "version": 1,
                    "vin": [
                        {
                            "txid": "2745c068857657574d60f88fa5913a7c0ba7a16261cdef86e8597ac89a1b1aa4",
                            "scriptSig": {
                                "hex": "483045022100e5a03dd3c45d96ec02efc28062c45401fa3b9b7ef59cdd4733e05f37a98f318c0220504dca1d50f8befa962a77d4f0221fb4306441f0f1d08bbf26c3a5b0f6bfc2cf0141040a5ef4d974163c9a75e3eb1576e3b9c45c81e52cef927419a67dea2433bd6a90729f5e31cfc83a2bdf885e543e008848716e9c4bd934e214681e4c8dd30858aa",
                                "asm": "3045022100e5a03dd3c45d96ec02efc28062c45401fa3b9b7ef59cdd4733e05f37a98f318c0220504dca1d50f8befa962a77d4f0221fb4306441f0f1d08bbf26c3a5b0f6bfc2cf01 040a5ef4d974163c9a75e3eb1576e3b9c45c81e52cef927419a67dea2433bd6a90729f5e31cfc83a2bdf885e543e008848716e9c4bd934e214681e4c8dd30858aa"
                            },
                            "sequence": 4294967295,
                            "vout": 0
                        }
                    ],
                    "locktime": 0,
                    "vout": [
                        {
                            "value": 0.1,
                            "scriptPubKey": {
                                "addresses": [
                                    "156ZGtQFT7R8dBQgX9BEZyzesiDrvk9UWg"
                                ],
                                "type": "pubkeyhash",
                                "reqSigs": 1,
                                "hex": "76a9142ced861a55f6c8d60df8d92625f63481aaf1c67988ac",
                                "asm": "OP_DUP OP_HASH160 2ced861a55f6c8d60df8d92625f63481aaf1c679 OP_EQUALVERIFY OP_CHECKSIG"
                            },
                            "n": 0
                        },
                        {
                            "value": 598.6,
                            "scriptPubKey": {
                                "addresses": [
                                    "1KsERhu5nqC9MwjAijecim57at1uqUakf7"
                                ],
                                "type": "pubkeyhash",
                                "reqSigs": 1,
                                "hex": "76a914cef2450598ec31718d7ce7a2d5fa0382c320666788ac",
                                "asm": "OP_DUP OP_HASH160 cef2450598ec31718d7ce7a2d5fa0382c3206667 OP_EQUALVERIFY OP_CHECKSIG"
                            },
                            "n": 1
                        }
                    ]
                }
        }
        self.register_call(response)
        r = self.sut.decode_raw_transaction('a_raw_transaction')
        json_response = json.loads(json.dumps(response), parse_float=Decimal)
        self.assertDictEqual(r, json_response)
        payload = json.loads(httpretty.last_request().body.decode('utf-8'))
        self.assertEqual(payload.get('method'), 'decoderawtransaction')
        self.assertEqual(payload.get('params')[0], 'a_raw_transaction')

    @httprettified
    def test_decode_raw_transaction_wrong_rawtx(self):
        response = {'error':{'message': 'TX Decode failed', 'code': -22}}
        self.register_call(response)
        with self.assertRaises(BitcoinCliException):
            self.sut.decode_raw_transaction('invalid_txhash')
        payload = json.loads(httpretty.last_request().body.decode('utf-8'))
        self.assertEqual(payload.get('method'), 'decoderawtransaction')
        self.assertEqual(payload.get('params')[0], 'invalid_txhash')

    @httprettified
    def test_get_block(self):
        response = {'result': {
            "hash" : "000000000000c5e7fb216de3593318708b3372afb511f3824c4a9f7300a39529",
            "confirmations" : 253627,
            "size" : 3263,
            "height" : 115002,
            "version" : 1,
            "merkleroot" : "edbcedc2619adbf21cee77ef0b943717da2bbea41c61296b04497e4590df303b",
            "tx" : [
                "0128d4ee91f5ccc61ef9ffe868a874f7b38a7e78cb7510cc576de989832d9345"
            ],
            "time" : 1301068491,
            "nonce" : 1630218460,
            "bits" : "1b00f339",
            "difficulty" : 68977.78463021,
            "chainwork" : "000000000000000000000000000000000000000000000000257e64bca853cb2b",
            "previousblockhash" : "0000000000007f51a1c13814ecb9698f56b91b2599552d7c47ec1d5b7517ae81",
            "nextblockhash" : "0000000000000f246cec2e9f71acc743db66da926a15cd31a2739612c64546dd"
        }}
        self.register_call(response)
        block_hash = '000000000000c5e7fb216de3593318708b3372afb511f3824c4a9f7300a39529'
        r = self.sut.get_block(block_hash)
        self.assertEqual(r['result'].get('hash'), block_hash)
        payload = json.loads(httpretty.last_request().body.decode('utf-8'))
        self.assertEqual(payload.get('method'), 'getblock')
        self.assertEqual(payload.get('params')[0], '000000000000c5e7fb216de3593318708b3372afb511f3824c4a9f7300a39529')

    @httprettified
    def test_get_block_invalid_hash(self):
        response = {'error':{"code":-5,"message":"Block not found"}}
        self.register_call(response)
        with self.assertRaises(BlockNotFound) as assertion:
            self.sut.get_block('invalid_block_hash')
        exception = assertion.exception
        self.assertEqual(exception.params, 'invalid_block_hash')
        self.assertEqual(exception.method, 'getblock')
        payload = json.loads(httpretty.last_request().body.decode('utf-8'))
        self.assertEqual(payload.get('method'), 'getblock')
        self.assertEqual(payload.get('params')[0], 'invalid_block_hash')

    @httprettified
    def test_get_block_hash(self):
        response = {"result": "block_hash"}
        self.register_call(response)
        r = self.sut.get_block_hash(123456)
        self.assertEqual(r, response)
        payload = json.loads(httpretty.last_request().body.decode('utf-8'))
        self.assertEqual(payload.get('method'), 'getblockhash')
        self.assertEqual(payload.get('params')[0], 123456)

    @httprettified
    def test_get_block_hash_invalid_height(self):
        response = {"error": {"code":-8,"message":"Block height out of range"}}
        #response = {'error':{"code":-5,"message":"Block not found"}}
        self.register_call(response)
        with self.assertRaises(BlockNotFound) as assertion:
            self.sut.get_block_hash(999999999)
        exception = assertion.exception
        self.assertEqual(exception.params, 999999999)
        self.assertEqual(exception.method, 'getblockhash')
        payload = json.loads(httpretty.last_request().body.decode('utf-8'))
        self.assertEqual(payload.get('method'), 'getblockhash')
        self.assertEqual(payload.get('params')[0], 999999999)

    @httprettified
    def test_get_raw_mempool(self):
        response = {'result': ["0002e85046f0a30502665aeedbe0c4d8995f5036706cd64b60d53e74cff321f7",
                    "000402b580749adf78b426b70be5e5cc852c3438365a23be9a51f68feede9063",
                    "0005fd7c4dbb05d00b3160024c3b40d962b89d27a4ce3b5016fc7ee7b922f844",
                    "00094dccfab0f4a730cda29b96104b02dfb693f762256b40d4656826a788deb4"]}
        self.register_call(response)
        r = self.sut.get_raw_mempool()
        self.assertEqual(r, response)
        payload = json.loads(httpretty.last_request().body.decode('utf-8'))
        self.assertEqual(payload.get('method'), 'getrawmempool')
        self.assertEqual(payload.get('params'), [])

    @httprettified
    def test_get_block_hash_unexpected_error(self):
        response = {"error": "Unexpected error"}
        self.register_call(response)
        with self.assertRaises(BitcoinCliException) as assertion:
            self.sut.get_block_hash(999999999)
        exception = assertion.exception
        self.assertEqual(exception.params[0], 999999999)
        self.assertEqual(exception.method, 'getblockhash')
        payload = json.loads(httpretty.last_request().body.decode('utf-8'))
        self.assertEqual(payload.get('method'), 'getblockhash')
        self.assertEqual(payload.get('params')[0], 999999999)