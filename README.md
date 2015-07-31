# bitcoincrawler
Completely customizable Bitcoin block parser, with asyncio support.
It is based on the Observer pattern.
Currently it scans 2.5 block/sec on single core Intel i5 2.4GHz

E.g.

```
class TXObserver(TransactionObserver):
  def on_transaction(self, tx):
    # Here you have a transaction

class InObserver(InputObserver):
  def on_input(self, input):
    # Here you have an input

class OutObserver(OutputObserver):
  def on_output(self, output):
    #¯Here you have an output
    
class BObserver(BlockObserver):
  def on_block(self, block):
    # Here you have a block

BTCD_USER = '<your bitcoind user name'
BTCD_PASSWD = '<your bitcoind password>'
BTCD_URL = "http://127.0.0.1:18332/"

btcd = BitcoinCli(BTCD_USER, BTCD_PASSWD, BTCD_URL)
node_backend = BitcoindBackend(btcd)
# The node generator is a generator that provides the required block.
# Here you get the first 50 blocks.
nodes_generator = node_backend.generate_blocks(height=509674, max_iterations=20, async=True)

bitcoin_scanner = BitcoinScanner(nodes_generator, node_backend, asyncio=asyncio.get_event_loop())
bitcoin_scanner.transactions_observers.append(TXObserver())
bitcon_scanner.blocks_observers.append(BObserver())
bitcoin_scanner.inputsobservers.append(InObserver())
bitcoin_scanner.outputsobservers.append(OutObserver())
bitcoin_scanner.mempool_inputsobservers.append(InObserver())
bitcoin_scanner.mempool_outputsobservers.append(OutObserver())

bitcoin_scanner.scan()
```