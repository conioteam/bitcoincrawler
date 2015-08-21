__author__ = 'guido'
import re
import json
from bitcoincrawler.components.bitcoind.client import BitcoinCli
from decimal import Decimal

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
            print(i)


if __name__ == '__main__':
    t = _TestsBuilder(BitcoinCli)
    t.parse_log('test.log')
    t.downloads_transactions()