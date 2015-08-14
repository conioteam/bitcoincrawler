from bitcoin import deserialize_script
from bitcoincrawler.components.pybitcointools.scripts import SCRIPTS
from bitcoin import pubtoaddr, hex_to_b58check
from decimal import Decimal
from bitcoincrawler.components.pybitcointools.exceptions.decoders import VoutDecoderException


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
            try:
                asm += '{}'.format(SCRIPTS[x])
            except:
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
    Experimental
    """
    @classmethod
    def __return_script(cls,
                      value=None,
                      n=None,
                      asm=None,
                      hex_script=None,
                      req_sigs=None,
                      script_type=None,
                      addresses=None):
        v = (Decimal(value) / Decimal(100000000)) if value else Decimal('0.00000000')
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
        data = {'hs': hex_script,
                'd': vout,
                'n': n,
                's': script,
                'p': {'pub': 0x00 if network == "main" else 0x6F,
                      'p2sh': 0x05 if network == "main" else 0xC4}}
        return VOUTDecoder.__decode(data)

    @classmethod
    def __decode(cls, data, script_type=None):
        addresses = []
        reqsigs = None
        if script_type != 'nonstandard':
            try:
                script_type = VOUTDecoder.get_script_type(data['s'])
                addresses = VOUTDecoder.get_addresses(data, script_type) if script_type != 'nonstandard' else []
                reqsigs = VOUTDecoder.get_reqsigs(data['s'], script_type) if addresses else None
            except VoutDecoderException:
                if script_type != "nonstandard":
                    return VOUTDecoder.__decode(data, script_type="nonstandard")
                else:
                    raise VoutDecoderException('_decode_nonstandard', 'recursive', data)
        asm = ''
        for i, b in enumerate(data['s']):
            try:
                asm += SCRIPTS[b]
            except KeyError:
                asm += str(b)
            if i < len(data['s'])-1: asm += ' '
        return VOUTDecoder.__return_script(value=Decimal('{}'.format(data['d']['value'])) \
                                                 if data['d']['value'] else None,
                                           n=data['n'],
                                           hex_script=data['hs'],
                                           asm=asm,
                                           addresses=addresses if addresses else None,
                                           req_sigs=reqsigs,
                                           script_type=script_type)

    @classmethod
    def get_addresses(cls, data, script_type):
        try:
            if script_type == "pubkeyhash" and len(data['s'][2]) == 40:
                return [hex_to_b58check(data['s'][2].encode('utf-8'), data['p']['pub'])]
            elif script_type == "scripthash" and len(data['s'][1]) == 40:
                return [hex_to_b58check(data['s'][1].encode('utf-8'), data['p']['p2sh'])]
            elif script_type == "multisig":
                return [pubtoaddr(data['s'][i].encode('utf-8')) for i in range(1, int(SCRIPTS[data['s'][-2]])+1)
                                  if isValidPubKey(data['s'][i])]
            elif script_type == "pubkey":
                return [pubtoaddr(data['s'][0].encode('utf-8'), 0x00)] if isValidPubKey(data['s'][0]) else []
        except (AttributeError, TypeError):
            raise VoutDecoderException('','','')
        return []

    @classmethod
    def get_reqsigs(cls, script, script_type):
        try:
            if script_type in ("pubkey", "pubkeyhash", "pubkey", "scripthash"):
                return 1
            elif script_type in ("multisig"):
                return int(SCRIPTS[script[0]])
        except:
            VoutDecoderException('','','')
        return None
        
    @classmethod
    def get_script_type(cls, script):
        try:
            if script[1] == 169 and script[-2] == 136 and script[-1] == 172 and len(script) == 5:
                return "pubkeyhash"
            elif script[0] == 106:
                return "nulldata"
            elif script[0] == 169 and script[2] == 135 and len(script) == 3:
                return "scripthash"
            elif script[1] == 172 and len(script[0]) in (66, 128, 130):
                return 'pubkey'
            elif script[-1] == 174 and script[-2] in range(1,21) and script[0] in range(1,21) \
                and len(script) == int(script[-2]) + 3:
                return 'multisig'
            else:
                return 'nonstandard'
        except (IndexError, KeyError):
            return 'nonstandard'
    
        
def isValidPubKey(pubkey):
    """
    https://github.com/bitcoin/bitcoin/blob/master/src/pubkey.h#L48
    # FIXME add rev
    """
    chHeader =  int(pubkey[:2], 16)
    if len(pubkey) == 66 and chHeader in (2,3) or \
        len(pubkey) == 130 and chHeader in (4,6,7):
        return True
    return False
