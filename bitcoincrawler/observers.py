__author__ = 'mirko'

class BlockObserver(object):
    def on_block(self, block):
        raise NotImplementedError

class TransactionObserver(object):
    def on_transaction(self, transaction):
        raise NotImplementedError

class InputObserver(object):
    def on_input(self, input):
        raise NotImplementedError

class OutputObserver(object):
    def on_output(self, output):
        raise NotImplementedError
