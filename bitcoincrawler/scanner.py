import asyncio

class BitcoinScanner:
    def __init__(self, blocks_generator, node_backend, async=False, mempool_storage=None):
        self.mempool_storage = mempool_storage
        self.blocks_generator = blocks_generator
        self.node_backend = node_backend
        self.blocks_observers = []
        self.inputs_observers = []
        self.outputs_observers = []
        self.transactions_observers = []
        self.mempool_transactions_observers = []
        self.mempool_inputs_observers = []
        self.mempool_outputs_observers = []
        self.transaction_left_mempool_observers = []
        self.inputs_left_mempool_observers = []
        self.outputs_left_mempool_observers = []
        if async:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = None

    def _notify_block(self, cur_block):
        for n in self.blocks_observers:
            n.on_block(cur_block)

    def _notify_transaction_blockchain_or_mempool(self, cur_tx, tx_observers, in_observers, out_observers):
        for n in tx_observers:
            if self.loop:
                self.loop.run_until_complete(asyncio.coroutine(lambda: n.on_transaction(cur_tx))())
            else:
                n.on_transaction(cur_tx)

        if len(in_observers) > 0:
            for vin in cur_tx.vin:
                for i_n in in_observers:
                    if self.loop:
                        self.loop.run_until_complete(asyncio.coroutine(lambda: i_n.on_input(vin))())
                    else:
                        i_n.on_input(vin)

        if len(out_observers) > 0:
            for vout in cur_tx.vout:
                for o_n in out_observers:
                    if self.loop:
                        self.loop.run_until_complete(asyncio.coroutine(lambda: o_n.on_output(vout))())
                    else:
                        o_n.on_output(vout)

    def notify_transaction(self, cur_tx):
        self._notify_transaction_blockchain_or_mempool(
            cur_tx, self.transactions_observers,
            self.inputs_observers, self.outputs_observers
        )
    def notify_transaction_left_mempool(self, cur_tx):
        self._notify_transaction_blockchain_or_mempool(
            cur_tx, self.transaction_left_mempool_observers,
            self.inputs_left_mempool_observers, self.outputs_left_mempool_observers
        )

    def notify_mempool_transaction(self, cur_tx):
        self._notify_transaction_blockchain_or_mempool(
            cur_tx, self.mempool_transactions_observers,
            self.mempool_inputs_observers, self.mempool_outputs_observers
        )
    def scan(self, mempool_limit=None):
        new_mempool = []
        notify_tx = lambda: len(self.transactions_observers) > 0 \
            or len(self.inputs_observers) > 0 \
            or len(self.outputs_observers) > 0

        notify_mempool_tx = lambda: len(self.mempool_transactions_observers) > 0 \
            or len(self.mempool_inputs_observers) > 0 \
            or len(self.mempool_outputs_observers) > 0

        notify_block = lambda: len(self.blocks_observers) > 0 or notify_tx

        notify_tx_left_mempool = lambda: len(self.transaction_left_mempool_observers) > 0 and \
                                         self.mempool_storage

        if notify_block:
            for cur_block in self.blocks_generator:
                self._notify_block(cur_block)
                if notify_tx:
                    for tx in cur_block.tx:
                        self.notify_transaction(tx)

        if notify_mempool_tx:
            new_mempool = self.node_backend.get_mempool_transactions(limit=mempool_limit)
            for cur_transaction in new_mempool:
                self.notify_mempool_transaction(cur_transaction)

        if notify_tx_left_mempool:
            new_mempool = self.node_backend.get_mempool_transactions(limit=mempool_limit) if not new_mempool else \
                new_mempool
            stored_mempool = self.mempool_storage.get()
            if not stored_mempool:
                self.mempool_storage.set(new_mempool)
            else:
                diff = [tx for tx in stored_mempool if tx not in new_mempool]
                for tx in diff:
                    self.notify_transaction_left_mempool(tx)
                self.mempool_storage.set(new_mempool)


class AsyncTaskException(Exception):
    def __init__(self, msg, method, params):
        Exception(self, msg)
        self._method = method
        self._params = params

    def getMethod(self):
        return self._method

    def getParams(self):
        return self._params