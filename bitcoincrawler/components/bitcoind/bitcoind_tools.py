from binascii import unhexlify
from scripts import SCRIPTS
from decimal import Decimal
from hashlib import sha256

try:
    from bitcoin.py3specials import bin_to_b58check
except:
    from bitcoin.py2specials import bin_to_b58check

from bitcoin import deserialize, deserialize_script

def hash_transaction(rawtx):
    b = sha256(sha256(unhexlify(rawtx)).digest()).digest()
    h = ''.join('{:02x}'.format(d) for d in b[::-1])
    return h

def decode_raw_transaction(rawtx, txid, parse=True):
    json_tx = {}
    d = deserialize(rawtx)
    json_tx['txid'] = txid
    json_tx['version'] = d['version']
    json_tx['locktime'] = d['locktime']
    json_tx['vin'] = []
    json_tx['vout'] = []
    if parse:
        for vin in d['ins']:
            ds = deserialize_script(vin['script'])
            dec = {'txid': vin['outpoint']['hash'],
                   'n': vin['outpoint']['index'],
                   'scriptSig': {'hex': vin['script'], 'asm': '{} {}'.format(ds[0], ds[1])},
                   'sequence': vin['sequence']}
            json_tx['vin'].append(dec)
        ii = 0

        for vout in d['outs']:
            addresses = []
            d_vout = deserialize_script(vout['script'])
            if d_vout[0] == 169:
                addr = bin_to_b58check(unhexlify(d_vout[1]))
                addresses.append(addr)
                asm = '{} {} {}'.format(SCRIPTS[d_vout[0]],
                                        addr,
                                        SCRIPTS[d_vout[2]])

            elif d_vout[0] in list(range(1, 21)): # Multisig
                asm = '{}'.format(SCRIPTS[d_vout[0]])
                for i in range(2, len(d_vout)-2):
                    addr = bin_to_b58check(unhexlify(d_vout[i]))
                    asm += ' {} '.format(addr)
                    addresses.append(addr)
                asm += '{}'.format(SCRIPTS[d_vout[len(d_vout)-1]])

            elif d_vout[0] == 106:  # OP_RETURN
                asm = '{} {}'.format(SCRIPTS[d_vout[0]],
                                             d_vout[1])
            else:
                addr = bin_to_b58check(unhexlify(d_vout[2]))
                addresses.append(addr)
                asm = '{0} {1} {2} {3} {4}'.format(SCRIPTS[d_vout[0]],
                                                   SCRIPTS[d_vout[1]],
                                                   addr,
                                                   SCRIPTS[d_vout[3]],
                                                   SCRIPTS[d_vout[4]])

            dec = {'value': '{0:.8f}'.format(Decimal(vout['value']) / Decimal(100000000)),
                   'n': ii,
                   'scriptPubKey': {'asm': asm,
                                    'hex': vout['script'],
                                    'reqSigs': len(addresses),
                                    'type': 0, # TODO
                                    'addresses': [None]} #TODO
                   }
            ii += 1
            json_tx['vout'].append(dec)
    return json_tx
