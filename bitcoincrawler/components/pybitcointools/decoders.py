from bitcoin import deserialize_script
from bitcoincrawler.components.pybitcointools.scripts import SCRIPTS
from bitcoin import pubtoaddr, hex_to_b58check
from decimal import Decimal

class VINDecoder:
    @classmethod
    def decode(cls, vin):
        if not int(vin['outpoint']['hash'], 16):
            return VINDecoder._decode_coinbase(vin)
        return VINDecoder._decode_script(vin)

    @classmethod
    def _decode_coinbase(cls, vin):
        return {'coinbase': vin['script'],
                'sequence': vin['sequence']}

    @classmethod
    def _decode_script(cls, vin):
        ds = [0 if x == None else x for x in deserialize_script(vin['script'])]
        asm = ''
        for i, x in enumerate(ds):
            asm += '{}'.format(x)
            if i < len(ds)-1:
                asm += ' '
        return {'txid': vin['outpoint']['hash'],
                'vout': vin['outpoint']['index'],
                'scriptSig': {'hex': vin['script'],
                              'asm': asm
                              },
                'sequence': vin['sequence']}

class VOUTDecoder:
    """
    This needs to be edited and compliant with the Bitcoin Scripting Language.
    Now catch only frequent cases.
    """
    @classmethod
    def __return_script(cls,
                      value=Decimal('0.00000000'),
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
    def decode(cls, vout, n, network):
        hex_script = vout['script']
        script = [0 if x == None else x for x in deserialize_script(hex_script)]
        data = {'d': vout,
                'n': n,
                's': script,
                'p': {'pub': 0x00 if network == "main" else 0x6F,
                      'p2sh': 0x05 if network == "main" else 0xC4}}
        try:
            if script[0] == 118 and script[1] == 169:
                decoder = VOUTDecoder._decode_PayToPubKeyHash
            elif script[0] == 169 and script[2] == 135:
                decoder = VOUTDecoder._decode_P2SH
            elif isinstance(script[0], str) and script[1] == 172:
                decoder = VOUTDecoder._decode_PayToPubKey
            elif script[0] == 106:
                decoder = VOUTDecoder._decode_OPRETURN
            elif script[-1] == 174:
                decoder = VOUTDecoder._decode_CHECKMULTISIG
            else:
                decoder = VOUTDecoder._decode_nonstandard
            return decoder(data)
        except (IndexError, AttributeError):
            return VOUTDecoder._decode_nonstandard(data)

    @classmethod
    def _decode_PayToPubKeyHash(cls, data):
        try:
            asm = '{} {} {} {} {}'.format(SCRIPTS[data['s'][0]],
                                       SCRIPTS[data['s'][1]],
                                       data['s'][2],
                                       SCRIPTS[data['s'][3]],
                                       SCRIPTS[data['s'][4]])
            return VOUTDecoder.__return_script(value='{0:.8f}'.format(Decimal(data['d']['value'])),
                                             n=data['n'],
                                             addresses=[hex_to_b58check(data['s'][2].encode('utf-8'), data['p']['pub']),],
                                             asm=asm,
                                             hex_script=data['d']['script'],
                                             req_sigs=1,
                                             script_type='pubkeyhash')
        except AttributeError:
            return VOUTDecoder._decode_nonstandard(data)

    @classmethod
    def _decode_OPRETURN(cls, data):
        try:
            asm = '{} {}'.format(SCRIPTS[data['s'][0]],
                                 data['s'][1] if data['s'][1] else '')
            return VOUTDecoder.__return_script(value=Decimal("0.0"),
                                             n=data['n'],
                                             asm=asm,
                                             hex_script=data['d']['script'],
                                             script_type='nulldata')
        except AttributeError:
            return VOUTDecoder._decode_nonstandard(data)

    @classmethod
    def _decode_P2SH(cls, data):
        try:
            asm = '{} {} {}'.format(SCRIPTS[data['s'][0]],
                                    data['s'][1],
                                    SCRIPTS[data['s'][2]])
            return VOUTDecoder.__return_script(value='{0:.8f}'.format(Decimal(data['d']['value'])),
                                             n=data['n'],
                                             addresses=[hex_to_b58check(data['s'][1].encode('utf-8'), data['p']['p2sh']),],
                                             asm=asm,
                                             hex_script=data['d']['script'],
                                             req_sigs=1,
                                             script_type='scripthash')
        except AttributeError:
            return VOUTDecoder._decode_nonstandard(data)

    @classmethod
    def _decode_CHECKMULTISIG(self, data):
        try:
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
            return VOUTDecoder.__return_script(value='{0:.8f}'.format(Decimal(data['d']['value'])),
                                             n=data['n'],
                                             addresses=addresses,
                                             asm=asm,
                                             hex_script=data['d']['script'],
                                             req_sigs=reqsigs if addresses else None,
                                             script_type="multisig")
        except AttributeError:
            return VOUTDecoder._decode_nonstandard(data)

    @classmethod
    def _decode_PayToPubKey(cls, data):
        try:
            b58_address = pubtoaddr(data['s'][0], 0x00)
            asm = '{} {}'.format(data['s'][0],
                                 SCRIPTS[data['s'][1]])
            return VOUTDecoder.__return_script(value='{0:.8f}'.format(Decimal(data['d']['value'])),
                                             n=data['n'],
                                             addresses=[b58_address,],
                                             asm=asm,
                                             hex_script=data['d']['script'],
                                             req_sigs=1,
                                             script_type='pubkey')
        except AttributeError:
            return VOUTDecoder._decode_nonstandard(data)

    @classmethod
    def _decode_nonstandard(cls, data):
        asm = ''
        fd = False
        for i, b in enumerate(data['s']):
            try:
                asm += SCRIPTS[b] if not fd else int(str(b).encode('utf-8'), 16)
                fd = (b in [169,] + list(range(1,75)))
            except (KeyError, TypeError):
                asm += str(b)
                fd = False
            if i < len(data['s'])-1: asm += ' '
        return VOUTDecoder.__return_script(value='{0:.8f}'.format(Decimal(data['d']['value'])),
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