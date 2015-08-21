__author__ = 'guido'
import re
import json
from bitcoincrawler.components.bitcoind.client import BitcoinCli
from bitcoincrawler.components.pybitcointools.model import PyBitcoinToolsTransaction
from decimal import Decimal
from collections import OrderedDict
from unittest import TestCase

BTCD_USER = 'bitcoinrpc'
BTCD_PASSWD = 'BPDuix1ptFkY1Yh2N6QFSjLwa3qRHC8xAdqrsbnYnV3J'
BTCD_URL = "http://127.0.0.1:8332/"

class fakefloat(float):
    def __init__(self, value):
        self._value = value
    def __repr__(self):
        return str(self._value)

def defaultencode(o):
    if isinstance(o, Decimal):
        # Subclass float with custom repr?
        return fakefloat(o)
    raise TypeError(repr(o) + " is not JSON serializable")


class _TestsBuilder:
    def __init__(self, client):
        self.txs = []
        self.btcd = client(BTCD_USER, BTCD_PASSWD, BTCD_URL, async=False)
        self.ptx = 0
        self.ttx = 0

    def parse_log(self, filename):
        with open(filename) as f:
            content = f.readlines()
        for x in content:
            y = re.search(r'\w{63,}', x)
            if y:
                self.txs.append(y.group())

    def downloads_transactions(self, t='bitcoind'):
        print('Total txs: {}'.format(len(self.txs)))
        for i, tx in enumerate(self.txs):
            with open('local/transactions/{}.json'.format(tx), 'w') as f:
                json.dump(self.btcd.decode_raw_transaction(self.btcd.get_raw_transaction(tx, async=False)['result'])['result'],
                          f,
                          default=defaultencode,
                          indent=2)


    def fetch_transaction(self, txid):
        def sort_json_as_bitcoind(dictionary):
            txsorted = OrderedDict([("txid", dictionary.get('txid')),
                                   ("version", dictionary.get("version")),
                                   ("locktime", dictionary.get("locktime")),
                                   ("vin", dictionary.get("vin")),
                                   ("vout", dictionary.get("vout"))])
            return json.dumps(txsorted, indent=2, default=defaultencode)

        rawtx = self.btcd.get_raw_transaction(txid).get('result')
        rpc_res = self.btcd.decode_raw_transaction(rawtx).get('result')
        rpc_decoded = sort_json_as_bitcoind(rpc_res)
        local_res = PyBitcoinToolsTransaction(rawtx, txid).json
        local_decoded = sort_json_as_bitcoind(local_res)
        self.compare(rpc_decoded, local_decoded)

    def compare(self, a, b):
        a = json.loads(a)
        b = json.loads(b)
        t = TestCase()
        t.maxDiff = None
        try:
            self.ttx += 1
            t.assertDictEqual(a, b)
            #print('compared {} : OK'.format(a['txid']))
        except AssertionError as e:
            self.ptx += 1
            print('[{} / {}] compared {} : FAILURE'.format(self.ptx, self.ttx, a['txid']))


if __name__ == '__main__':
    t = _TestsBuilder(BitcoinCli)
    t.parse_log('test.log')
    for tx in t.txs:
        t.fetch_transaction(tx)
