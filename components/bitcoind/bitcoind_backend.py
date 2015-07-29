import base64
import json
from decimal import Decimal
import requests
from components.node_backend import NodeBackend
from components.bitcoind.bitcoind_model import BTCDBlock, BTCDTransaction, BTCDVin, BTCDVout

class BitcoindBackend(NodeBackend):
    def __init__(self, btcd_user, btcd_password, btcd_url):
        self.btcd_url = btcd_url
        btcd_authpair = bytes(btcd_user.encode('utf-8')) + b':' + bytes(btcd_password.encode('utf-8'))
        btcd_auth_header = b'Basic ' + base64.b64encode(btcd_authpair)
        self.btcd_headers = {'content-type': 'application/json', 'Authorization': btcd_auth_header}

    def get_last_block_hash(self):
        return self.call('getbestblockhash')

    def get_missing_blocks(self, cur_block, margin_blocks):
        btc_block = self.call('getblockcount')

        if btc_block == cur_block:
            return

        starting_block_idx = cur_block - margin_blocks

        for i in range(starting_block_idx + 1, btc_block + 1):
            yield self.get_block(block_num=i)

    def call(self, method, *params):
        return self.__call(method, True, *params)

    def __call(self, method, jsonResponse, *params):
        payload = {
            'method': method,
            'params': params,
            'jsonrpc': '2.0',
            'id': 0,
        }
        response = requests.post(self.btcd_url, data=json.dumps(payload), headers=self.btcd_headers)
        if jsonResponse:
            response = json.loads(response.text, parse_float=Decimal)
        else:
            return response

        if response['error']:
            raise BitcoindException(response['error'], method, params)

        return response['result']

    def get_block(self, block_num=None, block_hash=None):
        if not block_hash:
            block_hash = self.call("getblockhash", block_num)
        return self.call("getblock", block_hash)

    def get_mempool_transactions(self):
        return (BTCDTransaction(self.call("decoderawtransaction",
                                          self.call("getrawtransaction", tx))) for tx in self.call("getrawmempool"))

    def get_raw_transaction(self, txid):
        return self.call("getrawtransaction", txid)

    def get_transaction(self, txid):
        return self.call("decoderawtransaction", self.call("getrawtransaction", txid))

    def get_vins_from_transaction(self, transaction_obj):
        return (BTCDVin(vin) for vin in transaction_obj.vin)

    def get_vouts_from_transaction(self, transaction_obj):
        return (BTCDVout(vout) for vout in transaction_obj.vout)

    def get_transactions_from_block(self, block_obj):
        return (BTCDTransaction(tx) for tx in block_obj.tx)

    def generate_blocks(self, hash=None, height=None, stop_hash=None, stop_height=None, max_iterations=None):
        if ((stop_height and stop_hash) or (stop_height and max_iterations) or (stop_hash and max_iterations)):
            raise ValueError('specify only one (and at least) stop condition',
                             'blocks_from',
                             'stop_hash: {}, stop_height: {}, max_iterations: {}'.format(stop_hash,
                                                                                         stop_height,
                                                                                         max_iterations))
        if hash and height != None or (not hash and height == None):
            raise ValueError('specify only one (and at least) hash or height',
                             'blocks_from',
                             'hash: {}, height: {}'.format(hash, height))
        if stop_height:
            stop_check = lambda i, block: block.height > stop_height
        elif max_iterations:
            stop_check = lambda i, block: i>= max_iterations
        else:
            stop_check = lambda i, block: block.hash == stop_hash
        i = 0
        hash = self.call("getblockhash", height) if not hash else hash
        while True:
            block = BTCDBlock(self.get_block(block_hash=hash), self)
            if stop_check(i, block):
                break
            yield block
            hash = block.nextblockhash
            i += 1

class BitcoindException(Exception):
    def __init__(self, msg, method, params):
        Exception(self, msg)
        self._method = method
        self._params = params

    def getMethod(self):
        return self._method

    def getParams(self):
        return self._params
