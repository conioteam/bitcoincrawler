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
    def __init__(self, btcd_user, btcd_password, btcd_url, async=False, async_limit=10):
        self.btcd_url = btcd_url
        btcd_authpair = bytes(btcd_user.encode("utf-8")) + b":" + bytes(btcd_password.encode("utf-8"))
        self.btcd_auth_header = b"Basic " + base64.b64encode(btcd_authpair)
        self.btcd_auth_header_async = "Basic " + base64.b64encode(btcd_authpair).decode('utf-8')
        if async and async_limit:
            self.async_lock = asyncio.Semaphore(async_limit)

    def call(self, method, *params, async=False, jsonResponse=True):
        try:
            return self.__call(method, *params, async=async, jsonResponse=jsonResponse)
        except ConnectionError:
            raise BitcoinCliException('', '', '')

    def __parse_res(self, r, method, params, jsonResponse=True):
        try:
            if jsonResponse:
                r = json.loads(r, parse_float=Decimal)
                if isinstance(r, dict) and r.get('error'):
                    raise BitcoinCliException(r["error"], "__call", str({"method": method,
                                                                   "params": params}))
                return r
            else:
                if '"error":' in r:
                    raise BitcoinCliException(json.loads(r)["error"], "__call", str({"method": method,
                                                                                   "params": params}))
                return r

        except ValueError as e:
            raise BitcoinCliException(e, method, params)

    @asyncio.coroutine
    def __aiohttp_routine(self, payload, jsonResponse=True):
        btcd_headers = {"content-type": "application/json", "Authorization": self.btcd_auth_header_async}
        with(yield from self.async_lock):
            r = yield from aiohttp.request('POST', self.btcd_url,
                                                   data=json.dumps(payload),
                                                   headers=btcd_headers)
            r = yield from r.text()

            return self.__parse_res(r, payload['method'], payload['params'], jsonResponse=jsonResponse)

    def __call(self, method, *params, async=False, jsonResponse=False):
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        if async:
            return self.__aiohttp_routine(payload, jsonResponse=jsonResponse)

        else:
            btcd_headers = {"content-type": "application/json", "Authorization": self.btcd_auth_header}
            res = requests.post(self.btcd_url,
                                data=json.dumps(payload),
                                headers=btcd_headers).text
            return self.__parse_res(res, method, params, jsonResponse=jsonResponse)
    
    def get_raw_transaction(self, txid, async=False, jsonResponse=False):
        try:
            if async:
                return chain(txid,
                             lambda txid: self.call("getrawtransaction", txid, async=async, jsonResponse=jsonResponse))
            else:
                return self.call("getrawtransaction", txid, jsonResponse=jsonResponse)
        except BitcoinCliException as btcde:
            if btcde.msg.get('code') == -5:
                raise TransactionNotFound(btcde.msg, 'getrawtransaction', txid)
            else:
                raise btcde

    def decode_raw_transaction(self, raw_transaction):
        return self.call("decoderawtransaction", raw_transaction)

    def get_and_decode_transaction(self, txid, async=False):
        """
        the bitcoincore gettransaction RPC call, often, is not enough.
        if you need it, you can use default_method
        :param txid:
        :return:
        """
        if async:
            return chain(txid,
                         lambda txid: self.call("getrawtransaction", txid, async=async),
                         lambda rawtx: self.call("decoderawtransaction", rawtx, async=async))
        else:
            return self.call("decoderawtransaction", self.call("getrawtransaction", txid))

    def get_block(self, block_hash):
        return self.call("getblock", block_hash)

    def get_block_hash(self, block_height):
        try:
            return self.call("getblockhash", block_height, jsonResponse=False)
        except BitcoinCliException as btcde:
            if btcde.msg.get('code') == -5:
                raise BlockNotFound(btcde.msg, 'getblockhash', block_height)
            else:
                raise btcde

    def get_raw_mempool(self):
        return self.call("getrawmempool")
