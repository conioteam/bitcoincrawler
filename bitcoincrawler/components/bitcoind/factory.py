import asyncio

from bitcoincrawler.components.base_factory import BaseFactory
from bitcoincrawler.components.bitcoind.model import BTCDBlock, BTCDTransaction
from bitcoincrawler.components.tools import chain


class BitcoindFactory(BaseFactory):
    def __init__(self, bitcoind_cli, async=False):
        """
        :param bitcoind_cli:
        :return:
        """
        self.btcd = bitcoind_cli
        self.async = async

    def get_mempool_transactions(self, limit=None):
        return self.get_transactions((self.btcd.get_raw_mempool()[:limit]) if limit else self.btcd.get_raw_mempool())

    def _get_transaction(self, txid):
        if self.async:
            return chain(txid,
                         lambda txid: self.btcd.get_and_decode_transaction(txid, async=True),
                         asyncio.coroutine(lambda json_tx: BTCDTransaction(json_tx)))
        else:
            return BTCDTransaction(self.btcd.get_and_decode_transaction(txid))

    def get_transactions(self, txs):
        if self.async:
            loop = asyncio.get_event_loop()
            tasks = (self._get_transaction(tx) for tx in txs)
            return loop.run_until_complete(asyncio.gather(*tasks))
        else:
            return (self._get_transaction(tx) for tx in txs)

    def generate_blocks(self, hash=None, height=None, stop_hash=None, stop_height=None, max_iterations=None, txs_factory=None):
        """
        A starting point is mandatory. Only one can be specified.
        Stop point is optional. Only one can be specified.
        :param hash: starting point (block hash)
        :param height: starting point (block height, 0 is valid).
        :param stop_hash: stop point (block hash)
        :param stop_height: stop point (block height)
        :param max_iterations: stop point (see this as "how many blocks I want to generate?")
        :param txs_factory: atm reserved to the adapter, if used # FIXME - review
        :return: BTCDBlock objects generator
        """
        if ((stop_height and stop_hash) or (stop_height and max_iterations) or (stop_hash and max_iterations)):
            raise ValueError('specify at most one stop condition',
                             'blocks_from',
                             'stop_hash: {}, stop_height: {}, max_iterations: {}'.format(stop_hash,
                                                                                         stop_height,
                                                                                         max_iterations))

        prev_hash = None
        if hash and height != None or (not hash and height == None):
            raise ValueError('specify only one (and at least) start condition',
                             'blocks_from',
                             'hash: {}, height: {}'.format(hash, height))
        if stop_height:
            stop_check = lambda i, block: block.height > stop_height
        elif max_iterations:
            stop_check = lambda i, block: i>= max_iterations
        else:
            stop_check = lambda i, block: prev_hash and (prev_hash == stop_hash)
        i = 0
        hash = self.btcd.get_block_hash(height) if not hash else hash

        while True:
            print('returning block')
            block = BTCDBlock(self.btcd.get_block(hash), self if not txs_factory else txs_factory)
            print('block returnered')
            if stop_check(i, block):
                break
            yield block
            prev_hash = block.hash
            hash = block.nextblockhash
            if not hash:
                break
            i += 1