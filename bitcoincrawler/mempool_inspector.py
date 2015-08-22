import asyncio

class MempoolInspector:
    def __init__(self, node_backend, async=True, limit=None):
        self.limit = limit
        self.node_backend = node_backend
        self.mempool_txs = {}
        self.transaction_join_mempool_observers = []
        self.inputs_join_mempool_observers = []
        self.outputs_join_mempool_observers = []
        self.transaction_part_mempool_observers = []
        self.inputs_part_mempool_observers = []
        self.outputs_part_mempool_observers = []

        if async:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = None

    def _notify_transaction(self, cur_tx, tx_observers, in_observers, out_observers):
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

    def notify_transaction_join_mempool(self, cur_tx):
        self._notify_transaction(
            cur_tx, self.transaction_join_mempool_observers,
            self.inputs_join_mempool_observers, self.outputs_join_mempool_observers
        )

    def notify_transaction_part_mempool(self, cur_tx):
        self._notify_transaction(
            cur_tx, self.transaction_part_mempool_observers,
            self.inputs_part_mempool_observers, self.outputs_part_mempool_observers
        )

    def inspect(self):
        notify_mempool_tx = lambda: len(self.transaction_join_mempool_observers) > 0 \
            or len(self.inputs_join_mempool_observers) > 0 \
            or len(self.outputs_join_mempool_observers) > 0

        notify_tx_part_mempool = lambda: len(self.transaction_part_mempool_observers) > 0 \
                                      or len(self.inputs_part_mempool_observers) > 0 \
                                      or len(self.outputs_part_mempool_observers) > 0

        if notify_mempool_tx():
            new_mempool = self.node_backend.btcd.get_raw_mempool().get('result')
            fetch = [txid for txid in new_mempool if txid not in self.mempool_txs.keys()]
            transactions = self.node_backend.get_transactions(fetch)
            for tx in transactions:
                self.mempool_txs[tx.txid] = tx
                self.notify_transaction_join_mempool(tx)
            if notify_tx_part_mempool():
                diff = [tx for tx in self.mempool_txs if tx not in new_mempool]
                for txid in diff:
                    self.notify_transaction_part_mempool(self.mempool_txs[txid])
                    self.mempool_txs.pop(txid)