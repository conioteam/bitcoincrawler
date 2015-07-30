from unittest import TestCase
from unittest.mock import Mock, call
from bitcoincrawler.bitcoin_scanner import BitcoinScanner

__author__ = 'mirko'

class TestBitcoinScanner(TestCase):
    def test_block_listener(self):

        block1 = Mock()
        block2 = Mock()
        block3 = Mock()
        blocks = [block1, block2, block3]

        def side_effect_get_block(block_num=-1):
            return blocks[block_num - 1]

        node_backend = Mock()
        node_backend.generate_blocks.side_effect = side_effect_get_block

        sut = BitcoinScanner([block1, block2, block3], node_backend)

        block_observer = Mock()

        sut.blocks_observers.append(block_observer)
        sut.scan()

        self.assertEqual(
            [call(block1), call(block2), call(block3)],
            block_observer.on_block.call_args_list)

    def test_tx_scanner(self):
        node_backend = Mock()
        block = Mock()
        node_backend.get_block.side_effect = lambda block_num: block

        tx1 = Mock()
        tx2 = Mock()
        tx3 = Mock()

        block = Mock()
        block.tx = [tx1, tx2, tx3]

        sut = BitcoinScanner([block], node_backend)

        tx_observer = Mock()
        sut.transactions_observers.append(tx_observer)

        sut.scan()

        self.assertEqual(
            [call(tx1), call(tx2), call(tx3)],
            tx_observer.on_transaction.call_args_list
        )

    def test_inout_scanner(self):
        node_backend = Mock()
        block = Mock()
        node_backend.get_block.side_effect = lambda block_num: block

        block = Mock()
        tx = Mock()
        block.tx = [tx]

        sut = BitcoinScanner([block], node_backend)

        in1 = Mock()
        in2 = Mock()

        tx.vin = [in1, in2]

        out1 = Mock()
        out2 = Mock()
        out3 = Mock()

        tx.vout = [out1, out2, out3]

        in_observer = Mock()
        out_observer = Mock()
        sut.inputs_observers.append(in_observer)
        sut.outputs_observers.append(out_observer)

        sut.scan()

        self.assertEqual(
            [call(in1), call(in2)],
            in_observer.on_input.call_args_list
        )

        self.assertEqual(
            [call(out1), call(out2), call(out3)],
            out_observer.on_output.call_args_list
        )


    def test_inout_mempool_scanner(self):
        node_backend = Mock()
        block = Mock()


        tx = Mock()

        node_backend.get_mempool_transactions.side_effect = lambda: [tx]

        sut = BitcoinScanner([], node_backend)

        in1 = Mock()
        in2 = Mock()

        tx.vin = [in1, in2]

        out1 = Mock()
        out2 = Mock()
        out3 = Mock()

        tx.vout = [out1, out2, out3]

        in_observer = Mock()
        out_observer = Mock()
        sut.mempool_inputs_observers.append(in_observer)
        sut.mempool_outputs_observers.append(out_observer)

        sut.scan()

        self.assertEqual(
            [call(in1), call(in2)],
            in_observer.on_input.call_args_list
        )

        self.assertEqual(
            [call(out1), call(out2), call(out3)],
            out_observer.on_output.call_args_list
        )

