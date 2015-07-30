__author__ = 'mirko'

class NodeBackend(object):
    def get_mempool_transactions(self):
        raise NotImplementedError

    def get_transaction(self, txid, async=False):
        raise NotImplementedError

    def generate_blocks(self,
                        hash=None, height=None,
                        stop_hash=None, stop_height=None, max_iterations=None,
                        async=False):
        raise NotImplementedError
