from bitcoincrawler.components.model import Transaction, Vin, Vout
from bitcoin import deserialize
from bitcoincrawler.components.pybitcointools.decoders import VOUTDecoder, VINDecoder

class PyBitcoinToolsTransaction(Transaction):
    def __init__(self, hextx, txid, meta=None):
        self._hex = hextx
        self._txid = txid
        self.__json_obj = None
        meta = meta if meta else dict()
        self.__parent_block = meta.get('parent_block')

    def _deserialize(self):
        if not self.__json_obj:
            self.__json_obj = deserialize(self._hex)

    @property
    def json(self):
        return self.__json_obj

    @property
    def is_coinbase(self):
        self._deserialize()
        return bool(VINDecoder.decode(self.__json_obj.get('ins')[0]).get('coinbase'))

    @property
    def txid(self):
        return self._txid

    @property
    def version(self):
        self._deserialize()
        return self.__json_obj.get('version')

    @property
    def locktime(self):
        self._deserialize()
        return self.__json_obj.get('locktime')

    @property
    def vin(self):
        self._deserialize()
        return (PyBitcoinToolsVin(vin, self.txid) for vin in self.__json_obj.get('ins'))

    @property
    def vout(self):
        self._deserialize()
        i = 0
        for vout in self.__json_obj.get('outs'):
            yield PyBitcoinToolsVout(vout, i, self.txid)
            i += 1

    @property
    def parent(self):
        return self.__parent_block

class PyBitcoinToolsVin(Vin):
    def __init__(self, vin, parent_tx):
        self.__json_obj = None
        self._vin = vin
        self.__parent_tx = parent_tx

    @property
    def json(self):
        return self.__json_obj

    @property
    def parent(self):
        return self.__parent_tx

    def _deserialize(self):
        if not self.__json_obj:
            self.__json_obj = VINDecoder.decode(self._vin)

    @property
    def scriptSig(self):
        self._deserialize()
        class ScriptSig:
            def __init__(self, up):
                self.up = up

            @property
            def hex(self):
                self.up._deserialize()
                try: return self.up._json_obj.get('scriptSig').get('hex')
                except AttributeError: return None

            @property
            def asm(self):
                try: return self.up._json_obj.get('scriptSig').get('asm')
                except AttributeError: return None

        return ScriptSig(self)

    @property
    def sequence(self):
        self._deserialize()
        return self.__json_obj.get('sequence')

    @property
    def vout(self):
        self._deserialize()
        return self.__json_obj.get('vout')

    @property
    def txid(self):
        self._deserialize()
        return self.__json_obj.get('txid')

    @property
    def coinbase(self):
        self._deserialize()
        return self.__json_obj.get('coinbase')

class PyBitcoinToolsVout(Vout):
    def __init__(self, vout, n, parent_tx):
        self.__json_obj = None
        self._vout = vout
        self._n = n
        self.__parent_tx = parent_tx

    @property
    def json(self):
        return self.__json_obj

    @property
    def parent(self):
        return self.__parent_tx

    def _deserialize(self):
        if not self.__json_obj:
            self.__json_obj = VOUTDecoder.decode(self._vout, self._n)

    @property
    def value(self):
        self._deserialize()
        return self.__json_obj.get('value')

    @property
    def n(self):
        self._deserialize()
        return self.__json_obj.get('n')

    @property
    def scriptPubKey(self):
        self._deserialize()
        class ScriptPubKey:
            def __init__(self, up):
                self.up = up
                self.up._deserialize()

            @property
            def asm(self):
                try: return self.up.json.get('scriptPubKey').get('asm')
                except AttributeError: return None

            @property
            def hex(self):
                try: return self.up.json.get('scriptPubKey').get('hex')
                except AttributeError: return None

            @property
            def reqSigs(self):
                try: return self.up.json.get('scriptPubKey').get('reqSigs')
                except AttributeError: return None

            @property
            def type(self):
                try: return self.up.json.get('scriptPubKey').get('type')
                except AttributeError: return None

            @property
            def addresses(self):
                try: return self.up.json.get('scriptPubKey').get('addresses')
                except AttributeError: return None
        return ScriptPubKey(self)
