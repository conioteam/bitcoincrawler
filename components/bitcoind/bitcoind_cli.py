__author__ = "guido"
import base64
import requests
import json
from decimal import Decimal

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
        btcd_auth_header = b"Basic " + base64.b64encode(btcd_authpair)
        self.btcd_headers = {"content-type": "application/json", "Authorization": btcd_auth_header}

    def call(self, method, *params):
        return self.__call(method, True, *params)

    def __call(self, method, jsonResponse, *params):
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        response = requests.post(self.btcd_url, data=json.dumps(payload), headers=self.btcd_headers)
        if jsonResponse:
            response = json.loads(response.text, parse_float=Decimal)
        else:
            return response

        if response["error"]:
            raise ValueError(response["error"], "__call", str({"method": method,
                                            "jsonResponse": jsonResponse}))

        return response["result"]
    
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

    def get_transaction(self, txid, default_method=False):
        """
        the bitcoincore gettransaction RPC call, often, is not enough.
        if you need it, you can use default_method
        :param txid:
        :return:
        """
        try:
            if default_method:
                return self.call("gettransaction", txid)
            return self.call("decoderawtransaction", self.call("getrawtransaction", txid))
        except Exception as e:
            raise BitcoindException(e, "decoderawtransaction", str({"txid": txid,
                                                                 "default_method": default_method}))
    
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