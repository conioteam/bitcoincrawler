import asyncio

@asyncio.coroutine
def chain(obj, *funcs):
    for f in funcs:
        obj = yield from f(obj)
    return obj