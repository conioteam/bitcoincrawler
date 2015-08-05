class BaseFactory:
    def _get_transaction(self, txid):
        raise NotImplementedError()

    def get_mempool_transactions(self):
        raise NotImplementedError()

    def get_transactions(self, txs):
        raise NotImplementedError()

    def generate_blocks(self,
                        hash=None,
                        height=None,
                        stop_hash=None,
                        stop_height=None,
                        max_iterations=None):
        raise NotImplementedError()


class AdapterFactory(BaseFactory):
    def __init__(self, txs_factory, blocks_factory):
        self.t = txs_factory
        self.b = blocks_factory

    def _get_transaction(self, txid):
        return self.t._get_transaction(self, txid)

    def get_mempool_transactions(self, limit=None):
        return self.t.get_mempool_transactions(limit=limit)

    def get_transactions(self, txs):
        return self.t.get_transactions(txs)

    def generate_blocks(self, hash=None, height=None, stop_hash=None, stop_height=None, max_iterations=None, txs_factory=None): # FIXME
        return self.b.generate_blocks(hash=hash,
                                      height=height,
                                      stop_hash=stop_hash,
                                      stop_height=stop_height,
                                      max_iterations=max_iterations,
                                      txs_factory=self.t)