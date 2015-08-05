__author__ = 'guido'

class Block:
    @property
    def hash(self):
        raise NotImplementedError()

    @property
    def height(self):
        raise NotImplementedError()

    @property
    def transactions(self):
        raise NotImplementedError()

    @property
    def coinbase(self):
        raise NotImplementedError()

    @property
    def timestamp(self):
        raise NotImplementedError()

class Transaction:
    @property
    def txid(self):
        raise NotImplementedError()

    @property
    def version(self):
        raise NotImplementedError()

    @property
    def locktime(self):
        raise NotImplementedError()

    @property
    def vin(self):
        raise NotImplementedError()

    @property
    def vout(self):
        raise NotImplementedError()

    @property
    def in_block(self):
        raise NotImplementedError()

class Vin:
    @property
    def scriptSig(self):
        class ScriptSig:
            @property
            def hex(self):
                raise NotImplementedError()

            @property
            def asm(self):
                raise NotImplementedError()

        return ScriptSig()

    @property
    def sequence(self):
        raise NotImplementedError()

    @property
    def vout(self):
        raise NotImplementedError()

    @property
    def txid(self):
        raise NotImplementedError()

class Vout:
    @property
    def value(self):
        raise NotImplementedError()

    @property
    def n(self):
        raise NotImplementedError()

    @property
    def scriptPubKey(self):
        class ScriptPubKey:
            @property
            def asm(self):
                raise NotImplementedError()

            @property
            def hex(self):
                raise NotImplementedError()

            @property
            def reqSigs(self):
                raise NotImplementedError()

            @property
            def type(self):
                raise NotImplementedError()

            @property
            def addresses(self):
                raise NotImplementedError()

        return ScriptPubKey()