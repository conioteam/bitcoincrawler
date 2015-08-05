from bitcoin import deserialize_script
from bitcoincrawler.components.pybitcointools.scripts import SCRIPTS
try:
    from bitcoin.py2specials import bin_to_b58check
except:
    from bitcoin.py3specials import bin_to_b58check

from decimal import Decimal
from binascii import unhexlify

class VINDecoder:
    @classmethod
    def decode(cls, vin):
        ds = deserialize_script(vin['script'])
        return {'txid': vin['outpoint']['hash'],
                'n': vin['outpoint']['index'],
                'scriptSig': {'hex': vin['script'],
                              'asm': '{} {}'.format(ds[0], ds[1])
                              },
                'sequence': vin['sequence']}

class VOUTDecoder:
    @classmethod
    def return_script(cls,
                      value=None,
                      n=None,
                      asm=None,
                      hex_script=None,
                      req_sigs=None,
                      script_type=None,
                      addresses=None):
        return {'value': '{0:.8f}'.format(Decimal(value) / Decimal(100000000)),
                'n': n,
                'scriptPubKey': {'asm': asm,
                                 'hex': hex_script,
                                 'reqSigs': req_sigs,
                                 'type': script_type,
                                 'addresses': addresses}
                }

    @classmethod
    def _decode_HASH160(cls, data):
        b58_address = bin_to_b58check(unhexlify(data['s'][1]))
        asm = '{} {} {}'.format(SCRIPTS[data['s'][0]],
                                b58_address,
                                SCRIPTS[data['s'][2]])
        return VOUTDecoder.return_script(value=data['d']['value'],
                                         n=data['n'],
                                         addresses=[b58_address,],
                                         asm=asm,
                                         hex_script=data['s'],
                                         req_sigs=1,
                                         script_type=None) # TODO
    @classmethod
    def _decode_OPRETURN(cls, data):
        asm = '{} {}'.format(SCRIPTS[data['s'][0]],
                             data['s'][1])
        return VOUTDecoder.return_script(value=0,
                                         n=data['n'],
                                         addresses=[],
                                         asm=asm,
                                         hex_script=data['s'],
                                         req_sigs=0,
                                         script_type=None) # TODO
    @classmethod
    def _decode_OP_INT(cls, data):
        asm = '{}'.format(SCRIPTS[data['s'][0]])
        addresses = []
        for i in range(2, len(data['s'])-2):
            addr = bin_to_b58check(unhexlify(data['s'][i]))
            asm += ' {} '.format(addr)
            addresses.append(addr)
        asm += '{}'.format(SCRIPTS[data['s'][len(data['s'])-1]])
        return VOUTDecoder.return_script(value=0,
                                 n=data['n'],
                                 addresses=addresses,
                                 asm=asm,
                                 hex_script=data['s'],
                                 req_sigs=data['s'][0],
                                 script_type=None) # TODO

    @classmethod
    def decode(cls, vout, n):
        hex_script = vout['script']
        script = deserialize_script(hex_script)
        if script[0] == 169:
            decoder = VOUTDecoder._decode_HASH160
        elif script[0] == 106:
            decoder = VOUTDecoder._decode_OPRETURN
        elif script[0] in list(range(1, 21)):
            decoder = VOUTDecoder._decode_OP_INT
        else:
            raise ValueError('Unknown script')

        return decoder({'d': vout,
                        'n': n,
                        's': script})