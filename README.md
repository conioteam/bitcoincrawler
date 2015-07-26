# bitcoincrawler
Completely customizable Bitcoin block parser.

It is based on the Observer pattern.

E.g.
class TXObserver(TransactionObserver):
  def on_transaction(self, tx):
    # Do something nice with that transaction

class InObserver(InputObserver):
  def on_input(self, input):
    # Here you have a transaction

class OutObserver(OutputObserver):
  def on_output(self, output):
    #¯Here you have an output
    
class BObserver(BlockObserver):
  def on_block(self, block):
    # Here you have a block
    


# The node generator is a generator that provides the required block numbers
nodes_generator = [10, 11, 12]
node_backend = BitcoindBackend('rpcuser', 'rpcpassword', 'http://mybitcoindurl:port')

bitcoin_scanner = BitcoinScanner(nodes_generator, node_backend)
bitcoin_scanner.transactions_observers.append(TXObserver())
bitcon_scanner.blocks_observers.append(BObserver())
bitcoin_scanner.inputsobservers.append(InObserver())
bitcoin_scanner.outputsobservers.append(OutObserver())
bitcoin_scanner.mempool_inputsobservers.append(InObserver())
bitcoin_scanner.mempool_outputsobservers.append(OutObserver())

bitcoin_scanner.scan()
