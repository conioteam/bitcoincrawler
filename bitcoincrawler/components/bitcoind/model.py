from bitcoincrawler.components.model import Block, Transaction, Vin, Vout


class BTCDBlock(Block):
    def __init__(self, json_obj, txs_factory):
        self.__json_obj = json_obj
        self.__txs_factory = txs_factory

    @property
    def hash(self):
        return self.__json_obj.get('hash')

    @property
    def size(self):
        return self.__json_obj.get('size')

    @property
    def height(self):
        return self.__json_obj.get('height')

    @property
    def version(self):
        return self.__json_obj.get('version')

    @property
    def merkleroot(self):
        return self.__json_obj.get('merkleroot')

    @property
    def tx(self):
        return self.__txs_factory.get_transactions(self.__json_obj.get('tx'),
                                                   parent_block=self.__json_obj['hash'])

    @property
    def time(self):
        return self.__json_obj.get('time')

    @property
    def coinbase(self):
        return next(self.__txs_factory.get_transactions([self.__json_obj.get('tx')[0],]))

    @property
    def nonce(self):
        return self.__json_obj.get('nonce')

    @property
    def bits(self):
        return self.__json_obj.get('bits')

    @property
    def difficulty(self):
        return self.__json_obj.get('difficulty')

    @property
    def chainwork(self):
        return self.__json_obj.get('chainwork')

    @property
    def previousblockhash(self):
        return self.__json_obj.get('previousblockhash')

    @property
    def nextblockhash(self):
        return self.__json_obj.get('nextblockhash')


class BTCDTransaction(Transaction):
    def __init__(self, json_obj, meta=None):
        """
        Thinking about a standard transaction, did you ever felt a lack of data?
        Be strict.
        """
        meta = meta if meta else dict()
        self.__parent_block = meta.get('parent_block')
        self.__json_obj = json_obj

    @property
    def is_coinbase(self):
        return bool(self.__json_obj.get('vin')[0].get('coinbase'))

    @property
    def txid(self):
        return self.__json_obj.get('txid')

    @property
    def version(self):
        return self.__json_obj.get('version')

    @property
    def locktime(self):
        return self.__json_obj.get('locktime')

    @property
    def vin(self):
        return (BTCDVin(vin, self) for vin in self.__json_obj.get('vin'))

    @property
    def vout(self):
        return (BTCDVout(vout, self) for vout in self.__json_obj.get('vout'))

    @property
    def parent(self):
        return self.__parent_block


class BTCDVin(Vin):
    def __init__(self, json_obj, parent_tx):
        self.__json_obj = json_obj
        self.__parent_tx = parent_tx

    @property
    def parent(self):
        return self.__parent_tx

    @property
    def scriptSig(self):
        j = self.__json_obj
        class ScriptSig:
            @property
            def hex(self):
                try: return j.get('scriptSig').get('hex')
                except AttributeError: return None

            @property
            def asm(self):
                try: return j.get('scriptSig').get('asm')
                except AttributeError: return None

        return ScriptSig()

    @property
    def sequence(self):
        return self.__json_obj.get('sequence')

    @property
    def vout(self):
        return self.__json_obj.get('vout')

    @property
    def txid(self):
        return self.__json_obj.get('txid')

    @property
    def coinbase(self):
        return self.__json_obj.get('coinbase')


class BTCDVout(Vout):
    def __init__(self, json_obj, parent_tx):
        self.__json_obj = json_obj
        self.__parent_tx = parent_tx

    @property
    def parent(self):
        return self.__parent_tx

    @property
    def value(self):
        return self.__json_obj.get('value')

    @property
    def n(self):
        return self.__json_obj.get('n')

    @property
    def scriptPubKey(self):
        j = self.__json_obj
        class ScriptPubKey:
            @property
            def asm(self):
                try: return j.get('scriptPubKey').get('asm')
                except AttributeError: return None

            @property
            def hex(self):
                try: return j.get('scriptPubKey').get('hex')
                except AttributeError: return None

            @property
            def reqSigs(self):
                try: return j.get('scriptPubKey').get('reqSigs')
                except AttributeError: return None

            @property
            def type(self):
                try: return j.get('scriptPubKey').get('type')
                except AttributeError: return None

            @property
            def addresses(self):
                try: return j.get('scriptPubKey').get('addresses')
                except AttributeError: return None

        return ScriptPubKey()