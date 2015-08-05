from bitcoincrawler.components.bitcoind.bitcoind_factory import BitcoindFactory, chain
from bitcoincrawler.components.pybitcointools.pybitcointools_model import PyBitcoinToolsTransaction
import asyncio

class PyBitcoinToolsFactory(BitcoindFactory):
    def __init__(self, bitcoind_cli, async=False):
        super(PyBitcoinToolsFactory, self).__init__(bitcoind_cli, async=async)

    def _get_transaction(self, txid):
        if self.async:
            return chain(txid,
                         lambda txid: self.btcd.get_raw_transaction(txid, async=True),
                         asyncio.coroutine(lambda json_tx: PyBitcoinToolsTransaction(json_tx, txid)))
        else:
            return PyBitcoinToolsTransaction(self.btcd.get_raw_transaction(txid), txid)