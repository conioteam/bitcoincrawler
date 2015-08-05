from bitcoincrawler.components.model import Transaction, Vin, Vout
from bitcoin import deserialize
from bitcoincrawler.components.pybitcointools.decoders import VOUTDecoder, VINDecoder
try:
    from bitcoin.py2specials import bin_to_b58check
except:
    from bitcoin.py3specials import bin_to_b58check


class PyBitcoinToolsTransaction(Transaction):
    def __init__(self, hextx, txid, in_block=None):
        self._hex = hextx
        self._txid = txid
        self.json = None
        self._in_block = in_block

    def _deserialize(self):
        if not self.json:
            self.json = deserialize(self._hex)

    @property
    def txid(self):
        return self._txid

    @property
    def version(self):
        self._deserialize()
        return self.json.get('version')

    @property
    def locktime(self):
        self._deserialize()
        return self.json.get('locktime')

    @property
    def vin(self):
        self._deserialize()
        return (PyBitcoinToolsVin(vin) for vin in self.json.get('ins'))

    @property
    def vout(self):
        self._deserialize()
        i = 0
        for vout in self.json.get('outs'):
            yield PyBitcoinToolsVout(vout, i)
            i += 1

    @property
    def in_block(self):
        return self._in_block

class PyBitcoinToolsVin(Vin):
    def __init__(self, vin):
        self.json_obj = None
        self._vin = vin

    def _deserialize(self):
        if not self.json:
            self.json = VINDecoder.decode(self._vin)

    @property
    def scriptSig(self):
        self._deserialize()
        class ScriptSig:
            def __init__(self, up):
                self.up = up
                self.up._deserialize()

            @property
            def hex(self):
                try: return self.up.get('scriptSig').get('hex')
                except AttributeError: return None

            @property
            def asm(self):
                try: return self.up.get('scriptSig').get('asm')
                except AttributeError: return None

        return ScriptSig(self)

    @property
    def sequence(self):
        return self.json_obj.get('sequence')

    @property
    def vout(self):
        return self.json_obj.get('vout')

    @property
    def txid(self):
        return self.json_obj.get('txid')

    @property
    def coinbase(self):
        return self.json_obj.get('coinbase')

class PyBitcoinToolsVout(Vout):
    def __init__(self, vout, n):
        self.json = None
        self._vout = vout
        self._n = n

    def _deserialize(self):
        if not self.json:
            self.json = VOUTDecoder.decode(self._vout, self._n)

    @property
    def value(self):
        return self.json.get('value')

    @property
    def n(self):
        return self.json.get('n')

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
