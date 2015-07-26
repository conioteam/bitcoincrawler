import base64
import json
from decimal import Decimal
import requests
from bitcoincrawler.node_backend import NodeBackend


__author__ = 'mirko'

class BitcoindBackend(NodeBackend):
    def __init__(self, btcd_user, btcd_password, btcd_url):
        self.btcd_url = btcd_url
        btcd_authpair = bytes(btcd_user, 'utf-8') + b':' + bytes(btcd_password, 'utf-8')
        btcd_auth_header = b'Basic ' + base64.b64encode(btcd_authpair)
        self.btcd_headers = {'content-type': 'application/json', 'Authorization': btcd_auth_header}

    def get_missing_blocks(self, cur_block, margin_blocks):
        btc_block = self.call('getinfo')['blocks']

        if btc_block == cur_block:
            return []

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

    def get_mempool_txs(self):
        mempool_tx_hashes = self.call("getrawmempool")

        for txid in mempool_tx_hashes:
            yield self.call("decoderawtransaction", self.call("getrawtransaction", txid))


    def get_inputs_from_transaction(self, tx):
        return tx['vin']

    def get_outputs_from_transaction(self, tx):
        return tx['vout']

    def get_transactions_from_block(self, block):
        block_tx_hashes = block['tx']
        for txid in block_tx_hashes:
            yield self.call("decoderawtransaction", self.call("getrawtransaction", txid))


class BitcoindException(Exception):
    def __init__(self, msg, method, params):
        Exception(self, msg)
        self._method = method
        self._params = params

    def getMethod(self):
        return self._method

    def getParams(self):
        return self._params
