import json
from decimal import Decimal
from unittest.mock import Mock
from asyncio import coroutine
from hashlib import md5
import asyncio

@asyncio.coroutine
def chain(obj, *funcs):
    for f in funcs:
        obj = yield from f(obj)
    return obj

import os
PREFIX = os.path.dirname(__file__) + '/'

def get_raw_mempool():
    with open(PREFIX + 'cli_files/rawmempool.json') as outfile:
        return {"result": json.load(outfile, parse_float=Decimal)}

def get_raw_transaction(txid, async=False):
    def openfile(txid):
        with open(PREFIX + 'cli_files/rawtransactions.json') as outfile:
            return {"result": json.load(outfile, parse_float=Decimal).get(txid)}
    if async:
        return coroutine(lambda: openfile(txid))()
    else:
        return openfile(txid)

def decode_raw_transaction(rawtx, async=False):
    def openfile(rawtx):
        name = (md5(rawtx.encode('utf-8')).hexdigest())
        with open(PREFIX + 'cli_files/transactions/{}.json'.format(name)) as outfile:
            print(outfile)
            return {"result": json.load(outfile, parse_float=Decimal)}
    if async:
        return coroutine(lambda: openfile(rawtx))()
    else:
        return openfile(rawtx)

def get_block_hash(block_height):
    block_height = str(block_height)
    with open(PREFIX + 'cli_files/blockhash.json') as outfile:
        return {"result": json.load(outfile, parse_float=Decimal).get(block_height)}

def get_block(block_hash):
    with open(PREFIX + 'cli_files/blocks/{}.json'.format(block_hash)) as outfile:
        return {"result": json.load(outfile, parse_float=Decimal)}

bitcoin_cli_mock = Mock()
bitcoin_cli_mock.get_raw_mempool.side_effect = get_raw_mempool
bitcoin_cli_mock.get_raw_transaction.side_effect = get_raw_transaction
bitcoin_cli_mock.decode_raw_transaction.side_effect = decode_raw_transaction
bitcoin_cli_mock.get_block_hash.side_effect = get_block_hash
bitcoin_cli_mock.get_block.side_effect = get_block