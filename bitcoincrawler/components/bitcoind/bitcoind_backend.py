from bitcoincrawler.components.node_backend import NodeBackend
from bitcoincrawler.components.bitcoind.bitcoind_model import BTCDBlock, BTCDTransaction, AsyncBTCDBlock
import asyncio

@asyncio.coroutine
def chain(obj, *funcs):
    for f in funcs:
        obj = yield from f(obj)
    return obj

class BitcoindBackend(NodeBackend):
    def __init__(self, bitcoind_cli):
        """
        :param bitcoind_cli:
        :return:
        """
        self.btcd = bitcoind_cli

    def get_mempool_transactions(self):
        return (BTCDTransaction(self.btcd.get_and_decode_transaction(tx)) for tx in self.btcd.get_raw_mempool())

    def get_transaction(self, txid, async=False, limit=10):
        if async:
            return chain(txid,
                         lambda txid: self.btcd.get_and_decode_transaction(txid, async=async),
                         asyncio.coroutine(lambda json_tx: BTCDTransaction(json_tx)))
        else:
            return BTCDTransaction(self.btcd.get_and_decode_transaction(txid))

    def generate_blocks(self, hash=None, height=None, stop_hash=None, stop_height=None, max_iterations=None,
                        async=False):
        """
        A starting point is mandatory. Only one can be specified.
        Stop point is optional. Only one can be specified.
        :param hash: starting point (block hash)
        :param height: starting point (block height, 0 is valid).
        :param stop_hash: stop point (block hash)
        :param stop_height: stop point (block height)
        :param max_iterations: stop point (see this as "how many blocks I want to generate?")
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
            if async:
                block = AsyncBTCDBlock(self.btcd.get_block(hash), self)
            else:
                block = BTCDBlock(self.btcd.get_block(hash), self)
            print('block returnered')
            if stop_check(i, block):
                break
            yield block
            prev_hash = block.hash
            hash = block.nextblockhash

            if not hash:
                break

            i += 1