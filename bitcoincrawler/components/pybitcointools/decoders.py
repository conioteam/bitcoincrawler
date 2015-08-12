from bitcoin import deserialize_script
from bitcoincrawler.components.pybitcointools.scripts import SCRIPTS
from bitcoin import pubtoaddr, hex_to_b58check
from decimal import Decimal

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
    """
    This needs to be edited and compliant with the Bitcoin Scripting Language.
    Now catch only frequent cases.
    """
    @classmethod
    def return_script(cls,
                      value=Decimal('0.0'),
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
        script = [0 if x == None else x for x in deserialize_script(hex_script)]
        if len(script) == 5 and script[0] == 118 and script[1] == 169 and isinstance(script[2], str) and \
                        len(script[2]) == 40:
            decoder = VOUTDecoder._decode_PayToPubKeyHash
        elif len(script) == 3 and script[0] == 169 and len(script[1]) == 40 and script[2] == 135:
            decoder = VOUTDecoder._decode_P2SH
        elif len(script) == 2 and not isinstance(script[0],int) and (len(script[0]) == 130 or len(script[0]) == 66) \
                and script[1] == 172:
            decoder = VOUTDecoder._decode_PayToPubKey
        elif script[0] == 106:
            decoder = VOUTDecoder._decode_OPRETURN
        elif script[0] in range(1, 21) and script[-1] == 174 and script[-2] in range(1, 21):
            decoder = VOUTDecoder._decode_CHECKMULTISIG
        elif len(script) == 1 and not isinstance(script[0],int):
            decoder = VOUTDecoder._decode_OPDATA_nonstandard
        else:
            decoder = VOUTDecoder._decode_unknown_script

        return decoder({'d': vout,
                        'n': n,
                        's': script})

    @classmethod
    def _decode_PayToPubKeyHash(cls, data):
        asm = '{} {} {} {} {}'.format(SCRIPTS[data['s'][0]],
                                   SCRIPTS[data['s'][1]],
                                   data['s'][2],
                                   SCRIPTS[data['s'][3]],
                                   SCRIPTS[data['s'][4]])
        return VOUTDecoder.return_script(value=Decimal(data['d']['value']),
                                         n=data['n'],
                                         addresses=[hex_to_b58check(data['s'][2].encode('utf-8'), 0x00),],
                                         asm=asm,
                                         hex_script=data['d']['script'],
                                         req_sigs=1,
                                         script_type='pubkeyhash')
    @classmethod
    def _decode_OPRETURN(cls, data):
        asm = '{} {}'.format(SCRIPTS[data['s'][0]],
                             data['s'][1] if data['s'][1] else '')
        return VOUTDecoder.return_script(value=Decimal("0.0"),
                                         n=data['n'],
                                         asm=asm,
                                         hex_script=data['d']['script'],
                                         script_type='nulldata')

    @classmethod
    def _decode_P2SH(cls, data):
        asm = '{} {} {}'.format(SCRIPTS[data['s'][0]],
                                data['s'][1],
                                SCRIPTS[data['s'][2]])
        return VOUTDecoder.return_script(value=Decimal(data['d']['value']),
                                         n=data['n'],
                                         addresses=[hex_to_b58check(data['s'][1].encode('utf-8'), 0x05),],
                                         asm=asm,
                                         hex_script=data['d']['script'],
                                         req_sigs=1,
                                         script_type='scripthash')

    @classmethod
    def _decode_CHECKMULTISIG(self, data):
        asm = '{}'.format(SCRIPTS[data['s'][0]])
        addresses = []
        howmany = int(SCRIPTS[data['s'][-2]])
        reqsigs = int(SCRIPTS[data['s'][0]])
        for i in range(1, howmany+1):
            if isValidPubKey(data['s'][i]):
                addresses.append(pubtoaddr(data['s'][i]))
            asm += ' {}'.format(data['s'][i])
        asm += ' {} {}'.format(SCRIPTS[data['s'][-2]],
                              SCRIPTS[data['s'][-1]])
        return VOUTDecoder.return_script(value=Decimal(data['d']['value']),
                                         n=data['n'],
                                         addresses=addresses,
                                         asm=asm,
                                         hex_script=data['d']['script'],
                                         req_sigs=reqsigs if addresses else None,
                                         script_type="multisig")

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

    @classmethod
    def _decode_OPDATA_nonstandard(cls, data):
        return VOUTDecoder.return_script(n=data['n'],
                                         hex_script=data['d']['script'],
                                         asm=data['s'][0],
                                         script_type='nonstandard')

    @classmethod
    def _decode_unknown_script(cls, data):
        asm = ''
        fd = False
        for i, b in enumerate(data['s']):
            try:
                asm += SCRIPTS[b] if not fd else int(str(b).encode('utf-8'), 16)
                fd = (b in [169,] + list(range(1,75)))
            except:
                asm += str(b)
                fd = False
            if i < len(data['s'])-1: asm += ' '
        return VOUTDecoder.return_script(value=Decimal(data['d']['value']),
                                         n=data['n'],
                                         hex_script=data['d']['script'],
                                         asm=asm,
                                         script_type='nonstandard')

def isValidPubKey(pubkey):
    """
    https://github.com/bitcoin/bitcoin/blob/master/src/pubkey.h#L48
    """
    chHeader =  int(pubkey[:2], 16)
    if len(pubkey) == 66 and chHeader in (2,3) or \
        len(pubkey) == 130 and chHeader in (4,6,7):
        return True
    return False