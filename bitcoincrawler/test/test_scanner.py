from unittest import TestCase
from bitcoincrawler import scanner
from mock import Mock

class TestScanner(TestCase):
    def setUp(self):
        self.node_backend = Mock()
        self.block_obj = Mock()
        self.tx_obj = Mock()
        self.tx_obj.vin = [('a','b'), ('a','b')]
        self.tx_obj.vout =[('a','b'), ('a','b')]
        self.block_obj.tx = [self.tx_obj]
        self.node_backend.get_mempool_transactions.side_effect = [self.tx_obj,]
        self.block_obs = Mock()
        self.block_obs.on_block.side_effect = [True for x in range(1,100)]
        self.block_obs.on_transaction.side_effect = [True for x in range(1,100)]
        self.block_obs.on_input.side_effect = [True for x in range(1,100)]
        self.block_obs.on_output.side_effect = [True for x in range(1,100)]

        self.mempool_obs = Mock()
        self.mempool_obs.on_transaction.side_effect = [True for x in range(1,100)]
        self.mempool_obs.on_input.side_effect = [True for x in range(1,100)]
        self.mempool_obs.on_output.side_effect = [True for x in range(1,100)]

        self.blockgen = [self.block_obj, self.block_obj, self.block_obj]
        self.sut = scanner.BitcoinScanner(self.blockgen, self.node_backend)

        self.sut.blocks_observers.append(self.block_obs)
        self.sut.transactions_observers.append(self.block_obs)
        self.sut.inputs_observers.append(self.block_obs)
        self.sut.outputs_observers.append(self.block_obs)

        self.sut.mempool_transactions_observers.append(self.mempool_obs)
        self.sut.mempool_inputs_observers.append(self.mempool_obs)
        self.sut.mempool_outputs_observers.append(self.mempool_obs)

    def tearDown(self):
        self.node_backend.reset_mock()
        self.block_obs.reset_mock()
        self.mempool_obs.reset_mock()

    def test___notify_block(self):
        pass