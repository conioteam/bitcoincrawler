# bitcoincrawler
Completely customizable Bitcoin block parser, with asyncio support.
It is based on the Observer pattern.
Currently it scans ~250 txs/sec on single core Intel i5 2.4GHz

E.g.

```
from bitcoincrawler.observers import *
from bitcoincrawler.components.bitcoind.client import *
from bitcoincrawler.components.bitcoind.factory import BitcoindFactory
from bitcoincrawler.components.pybitcointools.factory import PyBitcoinToolsFactory
from bitcoincrawler.bitcoin_scanner import *
from bitcoincrawler.components.base_factory import AdapterFactory
import time

class Observer():
    def __init__(self):
        self.data = {}

    def on_transaction(self, tx):
        try:
            self.data['transactions'] += 1
        except:
            self.data['transactions'] = 1

    def on_input(self, input):
        try:
            self.data['input'] += 1
        except:
            self.data['input'] = 1

    def on_output(self, input):
        try:
            self.data['output'] += 1
        except:
            self.data['output'] = 1

    def on_block(self, block):
        try:
            self.data['bl'] += 1
        except:
            self.data['bl'] = 1

obs = Observer()
mp = Observer()

BTCD_USER = '<your bitcoinrpc username>'
BTCD_PASSWD = '<your bitcoinrpc password>'
BTCD_URL = 'http://localhost:8332' # 18332 for testnet
ASYNC = True
btcd = BitcoinCli(BTCD_USER, BTCD_PASSWD, BTCD_URL)

blocks_factory = BitcoindFactory(btcd, async=ASYNC)
txs_factory = PyBitcoinToolsFactory(btcd, async=ASYNC)

def bind(adapter, mp_obs, obs):
  nodes_generator = adapter.generate_blocks(height=115000, max_iterations=5)
  bitcoin_scanner = BitcoinScanner(nodes_generator, adapter, asyncio=asyncio.get_event_loop())
  bitcoin_scanner.mempool_inputs_observers.append(mp_obs)
  bitcoin_scanner.mempool_outputs_observers.append(mp_obs)
  bitcoin_scanner.mempool_transactions_observers.append(mp_obs)
  bitcoin_scanner.transactions_observers.append(obs)
  bitcoin_scanner.inputs_observers.append(obs)
  bitcoin_scanner.outputs_observers.append(obs)
  bitcoin_scanner.blocks_observers.append(obs)
  return bitcoin_scanner

s = time.time()

adapter = AdapterFactory(txs_factory, blocks_factory)
# produce blocks with bitcoinrpc
# produce rawtransactions with bitcoinrpc
# decode rawtransactions with local python parser

bind(adapter, mp, obs).scan()
at = time.time() - s
res = '{} parser: {} txs scanned in {} blocks, {} txs from mempool, done in {}s ({} tx\s)'
print(res.format('local', obs.data['transactions'], obs.data['bl'], mp.data['transactions'], (at), (obs.data['transactions']+mp.data['transactions']) / at))

```
