from bitcoincrawler.components.bitcoind.client import *
from bitcoincrawler.components.bitcoind.factory import BitcoindFactory
from bitcoincrawler.components.pybitcointools.factory import PyBitcoinToolsFactory
from bitcoincrawler.blockchain_scanner import *
from bitcoincrawler.components.base_factory import AdapterFactory
import time
import json
import logging
from random import randint 
from hashlib import md5

LOG_FILENAME = 'test.log'
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.WARNING,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')

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

class Storage():
    def __init__(self):
        self.txz = {}
        self.successes = []
        self.failures = {}

class Observer():
        def __init__(self, storage, task=None):
            self.transactions = 0
            self.inputs = 0
            self.outputs = 0
            self.blocks = 0
            self.task = task
            self.txz = storage.txz
            self.successes = storage.successes
            self.failures = storage.failures

        def on_transaction(self, tx):
            self.transactions += 1
            if self.task == 'push':
                self.txz[tx.txid] = tx.json
            elif self.task == 'compare':
                r = json.dumps(tx.json, default=defaultencode)
                l = json.dumps(self.txz[tx.txid], default=defaultencode)
                tr = json.loads(r)
                tl = json.loads(l)
                match = bool(tl == tr)
                if randint(0,42*100) == 42:
                    logging.warning('[txid {}]: md5: l: {}, r: {}'.format(tx.txid,
                                                                          md5(l.encode('utf-8')).hexdigest(),
                                                                          md5(r.encode('utf-8')).hexdigest()))
                if match:
                    self.successes.append(1)
                else:
                    print('{} doesn\'t match'.format(tx.txid))
                    self.failures[tx.txid] = [tx.json, self.txz[tx.txid]]

        def on_input(self, input):
            self.inputs += 1

        def on_output(self, input):
            self.outputs += 1

        def on_block(self, block):
            if not self.blocks % 1000:
                logging.warning('[{}] - parsed block #{}'.format(self.task, start_height + self.blocks))
            self.blocks += 1
            print('new block: {}'.format(start_height + self.blocks))


def do(storage):
    logging.warning("Starting task from height {} to {}".format(start_height, start_height+increment-1))
    obs = Observer(storage, task='push')
    mp = Observer(storage)

    def bind(adapter, mp_obs, obs):
      nodes_generator = adapter.generate_blocks(blockheight=start_height, max_iterations=increment)
      bitcoin_scanner = BitcoinScanner(nodes_generator, async=ASYNC)
      bitcoin_scanner.transactions_observers.append(obs)
      bitcoin_scanner.blocks_observers.append(obs)
      return bitcoin_scanner

    s = time.time()
    adapter = AdapterFactory(txs_factory, blocks_factory)
    bind(adapter, mp, obs).scan()
    at1 = time.time() - s

    mp1 = Observer(storage)
    obs1 = Observer(storage, task='compare')
    s = time.time()
    adapter1 = AdapterFactory(blocks_factory, blocks_factory)

    bind(adapter1, mp1, obs1).scan()
    at2 = time.time() - s
    res = '{} parser: {} txs scanned in {} blocks, {} txs from mempool, done in {}s ({} tx\s)'
    #FIXME Useful to find parsing mistakes, but unreliable for timings, since the step 2 handles comparison

    logging.warning(res.format('async local', obs.transactions, obs.blocks, mp.transactions, (at1), (obs.transactions+mp.transactions) / at1))
    logging.warning(res.format('async btrpc', obs1.transactions, obs1.blocks, mp1.transactions, (at2), (obs1.transactions+mp1.transactions) / at2))
    logging.warning('Match: {} out of {} transactions'.format(len(storage.successes), len(storage.successes)+len(list(storage.failures.keys()))))

BTCD_USER = '<<your username>>'
BTCD_PASSWD = '<<your password>>'
BTCD_URL = "http://127.0.0.1:8332/"
ASYNC = True
btcd = BitcoinCli(BTCD_USER, BTCD_PASSWD, BTCD_URL, async=ASYNC, async_limit=100)

blocks_factory = BitcoindFactory(btcd, async=ASYNC)
txs_factory = PyBitcoinToolsFactory(btcd, async=ASYNC)

if __name__ == '__main__':
    start_height = 1
    increment = 5
    storage = Storage()
    while start_height < 370000:
        do(storage)
        start_height += increment
