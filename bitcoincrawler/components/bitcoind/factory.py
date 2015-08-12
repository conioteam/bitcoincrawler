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
        self.network = bitcoind_cli.network

    def get_mempool_transactions(self, limit=None):
        mempool = self.btcd.get_raw_mempool().get('result')
        return self.get_transactions((mempool[:limit]) if limit else mempool)

    def _get_transaction(self, txid, parent_block=None):
        meta = {'parent_block': parent_block}
        if self.async:
            return chain(txid,
                         lambda txid: self.btcd.get_raw_transaction(txid, async=True),
                         lambda rawtx: self.btcd.decode_raw_transaction(rawtx.get('result'), async=True),
                         asyncio.coroutine(lambda json_obj: BTCDTransaction(json_obj.get('result'),
                                                                            meta=meta)))
        else:
            rawtx = self.btcd.get_raw_transaction(txid)
            json_obj = self.btcd.decode_raw_transaction(rawtx.get('result'))
            return BTCDTransaction(json_obj.get('result'))

    def get_transactions(self, txs, parent_block=None):
        if self.async:
            loop = asyncio.get_event_loop()
            tasks = (self._get_transaction(tx, parent_block=parent_block) for tx in txs)
            return loop.run_until_complete(asyncio.gather(*tasks))
        else:
            return (self._get_transaction(tx) for tx in txs)

    def generate_blocks(self, blockhash=None,
                        blockheight=None,
                        stop_blockhash=None,
                        stop_blockheight=None,
                        max_iterations=None,
                        txs_factory=None):
        """
        A starting point is mandatory. Only one can be specified.
        Stop point is optional. Only one can be specified.
        :param blockhash: starting point (block hash)
        :param blockheight: starting point (block height, 0 is valid).
        :param stop_blockhash: stop point (block hash)
        :param stop_blockheight: stop point (block height)
        :param max_iterations: stop point (see this as "how many blocks I want to generate?")
        :param txs_factory: atm reserved to the adapter, if used # FIXME - review
        :return: BTCDBlock objects generator
        """
        if ((stop_blockheight and stop_blockhash) or (stop_blockheight and max_iterations) or (stop_blockhash and max_iterations)):
            raise ValueError('specify at most one stop condition',
                             'blocks_from',
                             'stop_hash: {}, stop_height: {}, max_iterations: {}'.format(stop_blockhash,
                                                                                         stop_blockheight,
                                                                                         max_iterations))

        if blockhash and blockheight != None or (not blockhash and blockheight == None):
            raise ValueError('specify only one (and at least) start condition',
                             'blocks_from',
                             'hash: {}, height: {}'.format(blockhash, blockheight))

        def generator(blockhash=None,
                      blockheight=None,
                      stop_blockhash=None,
                      stop_blockheight=None,
                      max_iterations=None,
                      txs_factory=None):
            prev_hash = None
            if stop_blockheight:
                stop_check = lambda i, block: block.height > stop_blockheight
            elif max_iterations:
                stop_check = lambda i, block: i>= max_iterations
            else:
                stop_check = lambda i, block: prev_hash and (prev_hash == stop_blockhash)
            i = 0

            blockhash = self.btcd.get_block_hash(blockheight).get('result') if not blockhash else blockhash
            print('producing blocks...')
            while True:
                jsonblock = self.btcd.get_block(blockhash).get('result')
                block = BTCDBlock(jsonblock, self if not txs_factory else txs_factory)
                if stop_check(i, block):
                    break
                yield block
                prev_hash = block.hash
                blockhash = block.nextblockhash
                if not blockhash:
                    break
                i += 1

        return generator(blockhash=blockhash,
                         blockheight=blockheight,
                         stop_blockhash=stop_blockhash,
                         stop_blockheight=stop_blockheight,
                         max_iterations=max_iterations,
                         txs_factory=txs_factory)