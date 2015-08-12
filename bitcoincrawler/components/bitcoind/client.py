from bitcoincrawler.components.bitcoind.exceptions.client import BitcoinCliException, TransactionNotFound, \
    BlockNotFound

import base64
import asyncio
import requests
import json
from decimal import Decimal

from bitcoincrawler.components.tools import chain
import aiohttp
from requests.exceptions import ConnectionError

class BitcoinCli:
    """
    bitcoind v0.11
    """
    def __init__(self, btcd_user, btcd_password, btcd_url, async=False, async_limit=100):
        self.btcd_url = btcd_url
        btcd_authpair = bytes(btcd_user.encode("utf-8")) + b":" + bytes(btcd_password.encode("utf-8"))
        self.btcd_auth_header = b"Basic " + base64.b64encode(btcd_authpair)
        self.btcd_auth_header_async = "Basic " + base64.b64encode(btcd_authpair).decode('utf-8')
        if async and async_limit:
            self.async_lock = asyncio.Semaphore(async_limit)

    def call(self, method, *params, async=False):
        try:
            return self.__call(method, *params, async=async)
        except ConnectionError:
            raise BitcoinCliException('', '', '')

    def __parse_res(self, r, method, params):
        try:
            r = json.loads(r, parse_float=Decimal)
            if isinstance(r, dict) and r.get('error'):
                raise BitcoinCliException(r["error"], method, params)
            elif isinstance(r, list) and method == 'getrawmempool':
                return r
            return r
        except ValueError as e:
            raise BitcoinCliException(e, method, params)

    @asyncio.coroutine
    def __aiohttp_routine(self, payload):
        btcd_headers = {"content-type": "application/json", "Authorization": self.btcd_auth_header_async}
        with(yield from self.async_lock):
            r = yield from aiohttp.request('POST', self.btcd_url,
                                                   data=json.dumps(payload),
                                                   headers=btcd_headers)
            r = yield from r.text()

            return self.__parse_res(r, payload['method'], payload['params'])

    def __call(self, method, *params, async=False):
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        if async:
            return self.__aiohttp_routine(payload)
        else:
            btcd_headers = {"content-type": "application/json", "Authorization": self.btcd_auth_header}
            res = requests.post(self.btcd_url,
                                data=json.dumps(payload),
                                headers=btcd_headers).text
            return self.__parse_res(res, method, params)
    
    def get_raw_transaction(self, txid, async=False):
        try:
            if async:
                return chain(txid, lambda txid: self.call("getrawtransaction", txid, async=async))
            else:
                return self.call("getrawtransaction", txid)
        except BitcoinCliException as btcde:
            if isinstance(btcde.msg, dict) and btcde.msg.get('code') == -5:
                raise TransactionNotFound(btcde.msg, 'getrawtransaction', txid)
            else:
                raise btcde

    def decode_raw_transaction(self, raw_transaction, async=False):
        if async:
            return chain(raw_transaction,
                         lambda txid: self.call("decoderawtransaction", raw_transaction, async=async))
        else:
            return self.call("decoderawtransaction", raw_transaction)

    def get_block(self, block_hash):
        try:
            return self.call("getblock", block_hash)
        except BitcoinCliException as btcde:
            if btcde.msg.get('code') == -5:
                raise BlockNotFound(btcde.msg, 'getblock', block_hash)
            else:
                raise btcde

    def get_block_hash(self, block_height):
        try:
            return self.call("getblockhash", block_height)
        except BitcoinCliException as btcde:
            try:
                if isinstance(btcde.msg, dict) and btcde.msg.get('code') == -8:
                    raise BlockNotFound(btcde.msg, 'getblockhash', block_height)
                else:
                    raise btcde
            except AttributeError:
                raise btcde

    def get_raw_mempool(self):
        return self.call("getrawmempool")
