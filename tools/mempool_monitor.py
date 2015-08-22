import time
from bitcoincrawler.mempool_inspector import MempoolInspector

from bitcoincrawler.components.bitcoind.client import BitcoinCli
from bitcoincrawler.components.pybitcointools.factory import PyBitcoinToolsFactory


class Observer:
    def __init__(self, storage):
        self.action = 'joined'
        self.storage = storage
        self.storage['total'] = 0

    def on_transaction(self, tx):
        if self.action == 'joined':
            self.storage['total'] += 1
        elif self.action == 'part':
            self.storage['total'] -= 1
        msg = '[{}] new transaction {} the mempool: {}, total {}'
        print(msg.format(int(time.time()), self.action, tx.txid, self.storage.get('total')))

    def on_input(self, vin):
        msg = '[{}] new input {} mempool: {}'.format(int(time.time()), self.action, vin)
        print(msg)

    def on_output(self, vout):
        msg = '[{}] new output {} the mempool: {}'.format(int(time.time()), self.action, vout)
        print(msg)

storage = {}
joinMempool = Observer(storage)
partMempool = Observer(storage)
partMempool.action = 'part'
BTCD_USER = 'bitcoinrpc'
BTCD_PASSWD = 'BPDuix1ptFkY1Yh2N6QFSjLwa3qRHC8xAdqrsbnYnV3J'
BTCD_URL = "http://127.0.0.1:8332/"
ASYNC = True
btcd = BitcoinCli(BTCD_USER, BTCD_PASSWD, BTCD_URL, async=ASYNC, async_limit=100)
backend = PyBitcoinToolsFactory(btcd, async=ASYNC)

inspector = MempoolInspector(backend, async=True)
inspector.transaction_join_mempool_observers.append(joinMempool)
inspector.transaction_part_mempool_observers.append(partMempool)

def inspect_mempool():
    while True:
        inspector.inspect()
        time.sleep(0.5)

if __name__ == '__main__':
    inspect_mempool()