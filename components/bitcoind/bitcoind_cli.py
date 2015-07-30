__author__ = "guido"
import base64
import requests
import json
from decimal import Decimal
from components.bitcoind.bitcoind_backend import chain
from asyncio import coroutine
import aiohttp

class BitcoindException(Exception):
    def __init__(self, msg, method, params):
        Exception(self, msg)
        self._method = method
        self._params = params

    def getMethod(self):
        return self._method

    def getParams(self):
        return self._params

class BitcoinCli:
    """
    bitcoind v0.11
    """
    def __init__(self, btcd_user, btcd_password, btcd_url):
        self.btcd_url = btcd_url
        btcd_authpair = bytes(btcd_user.encode("utf-8")) + b":" + bytes(btcd_password.encode("utf-8"))
        self.btcd_auth_header = b"Basic " + base64.b64encode(btcd_authpair)
        self.btcd_auth_header_async = "Basic " + base64.b64encode(btcd_authpair).decode('utf-8')

    def call(self, method, *params, async=False):
        return self.__call(method, True, *params, async=async)

    def __call(self, method, jsonResponse, *params, async=False):
        def parse_res(r):
            print('parse_res: %s' % method)
            if jsonResponse:
                r = json.loads(r, parse_float=Decimal)
            else:
                return r

            if r["error"]:
                raise ValueError(r["error"], "__call", str({"method": method,
                                                "jsonResponse": jsonResponse}))
            return r["result"]

        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        if async:
            btcd_headers = {"content-type": "application/json", "Authorization": self.btcd_auth_header_async}
            print('preparing aiohttp chain')
            return chain(None,
                         lambda x: aiohttp.request('POST', self.btcd_url,
                                                   data=json.dumps(payload),
                                                   headers=btcd_headers),
                         lambda r: r.text(),
                         coroutine(lambda r: parse_res(r)))
        else:
            btcd_headers = {"content-type": "application/json", "Authorization": self.btcd_auth_header}
            res = requests.post(self.btcd_url,
                                data=json.dumps(payload),
                                headers=btcd_headers).text
            return parse_res(res)
    
    def get_raw_transaction(self, txid):
        try:
            return self.call("getrawtransaction", txid)
        except Exception as e:
            raise BitcoindException(e, "getrawtransaction", txid)

    def decode_raw_transaction(self, raw_transaction):
        try:
            return self.call("decoderawtransaction", raw_transaction)
        except Exception as e:
            raise BitcoindException(e, "decoderawtransaction", raw_transaction)

    def get_and_decode_transaction(self, txid, async=False):
        """
        the bitcoincore gettransaction RPC call, often, is not enough.
        if you need it, you can use default_method
        :param txid:
        :return:
        """
        try:
            if async:
                return chain(txid,
                             lambda txid: self.call("getrawtransaction", txid, async=async),
                             lambda rawtx: self.call("decoderawtransaction", rawtx, async=async))
            else:
                return self.call("decoderawtransaction", self.call("getrawtransaction", txid))
        except Exception as e:
            raise BitcoindException(e, "decoderawtransaction", txid)

    def get_transaction(self, txid):
        return self.call("gettransaction", txid)

    def get_best_block_hash(self):
        try:
            return self.call("getbestblockhash")
        except Exception as e:
            raise BitcoindException(e, "getbestblockhash", "")

    def get_block(self, block_hash):
        try:
            return self.call("getblock", block_hash)
        except Exception as e:
            raise BitcoindException(e, "getblock", block_hash)
    
    def get_block_hash(self, block_height):
        try: 
            return self.call("getblockhash", block_height)
        except Exception as e:
            raise BitcoindException(e, "getrawtransaction", block_height)

    def get_raw_mempool(self):
        try:
            return self.call("getrawmempool")
        except Exception as e:
            raise BitcoindException(e, "getrawtransaction", "")