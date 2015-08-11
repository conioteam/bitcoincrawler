from bitcoin import deserialize_script
from bitcoincrawler.components.pybitcointools.scripts import SCRIPTS
try:
    from bitcoin.py2specials import bin_to_b58check
except:
    from bitcoin.py3specials import bin_to_b58check

from bitcoin import pubtoaddr

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
        v = (Decimal(value) / Decimal(100000000)) if value else value
        r = {'value': v,
                'n': n,
                'scriptPubKey': {'asm': asm,
                                 'hex': hex_script,
                                 'type': script_type}
                }
        if req_sigs != None: r['scriptPubKey']['reqSigs'] = req_sigs
        if addresses != None: r['scriptPubKey']['addresses'] = addresses
        return r

    @classmethod
    def decode(cls, vout, n):
        hex_script = vout['script']
        script = deserialize_script(hex_script)
        print(script)
        if script[0] == 118 and script[1] == 169 and len(script) == 5 and len(script[2]) == 40:
            decoder = VOUTDecoder._decode_PayToPubKeyHash
        elif script[0] == 169 and len(script) == 3 and len(script[1]) == 40:
            decoder = VOUTDecoder._decode_P2SH
        elif not isinstance(script[0],int) and (len(script[0]) == 130 or len(script[0]) == 66) and script[1] == 172:
            decoder = VOUTDecoder._decode_PayToPubKey
        elif script[0] == 106:
            decoder = VOUTDecoder._decode_OPRETURN
        elif script[0] in range(1, 21):
            decoder = VOUTDecoder._decode_OP_INT
        else:
            raise ValueError('Unknown script') # TODO

        return decoder({'d': vout,
                        'n': n,
                        's': script})

    @classmethod
    def _decode_PayToPubKeyHash(cls, data):
        b58_address = bin_to_b58check(unhexlify(data['s'][2]))
        asm = '{} {} {} {} {}'.format(SCRIPTS[data['s'][0]],
                                   SCRIPTS[data['s'][1]],
                                   data['s'][2],
                                   SCRIPTS[data['s'][3]],
                                   SCRIPTS[data['s'][4]])
        return VOUTDecoder.return_script(value=Decimal(data['d']['value']),
                                         n=data['n'],
                                         addresses=[b58_address,],
                                         asm=asm,
                                         hex_script=data['d']['script'],
                                         req_sigs=1,
                                         script_type='pubkeyhash')
    @classmethod
    def _decode_OPRETURN(cls, data):
        asm = '{} {}'.format(SCRIPTS[data['s'][0]],
                             data['s'][1])
        return VOUTDecoder.return_script(value=Decimal("0.0"),
                                         n=data['n'],
                                         asm=asm,
                                         hex_script=data['d']['script'],
                                         script_type='nulldata')

    @classmethod
    def _decode_P2SH(cls, data):
        b58_address = bin_to_b58check(unhexlify(data['s'][1]), 0x05)
        asm = '{} {} {}'.format(SCRIPTS[data['s'][0]],
                                   data['s'][1],
                                   SCRIPTS[data['s'][2]])
        return VOUTDecoder.return_script(value=Decimal(data['d']['value']),
                                         n=data['n'],
                                         addresses=[b58_address,],
                                         asm=asm,
                                         hex_script=data['d']['script'],
                                         req_sigs=1,
                                         script_type='scripthash')
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
    def _decode_PayToPubKey(cls, data):
        b58_address = pubtoaddr(data['s'][0], 0x00)
        asm = '{} {}'.format(data['s'][0],
                             SCRIPTS[data['s'][1]])
        return VOUTDecoder.return_script(value=Decimal(data['d']['value']),
                                 n=data['n'],
                                 addresses=[b58_address,],
                                 asm=asm,
                                 hex_script=data['d']['script'],
                                 req_sigs=1,
                                 script_type='pubkey')
