from ec import ECPoint, FQ
from py_ecc.fields.field_elements import FQ2
from py_ecc.fields.optimized_field_elements import FQ as optimized_FQ, FQ2 as optimized_FQ2
from py_ecc.fields.field_elements import FQ as py_ecc_FQ
from py_ecc.optimized_bn128 import FQ as optimized_bn128_FQ, normalize

# TODO: input to serialize
MAX_INT_SIZE = 32 # bytes

class SerializationError(Exception):
    pass

def serialize(*args) -> bytes:
    b = b""
    for i in range(len(args)):
        assert args[i] is not None
        if type(args[i]) is int:
            b += args[i].to_bytes(MAX_INT_SIZE, 'big')
        elif issubclass(type(args[i]), FQ) or issubclass(type(args[i]), optimized_FQ):
            b += serialize(args[i].n)
        elif issubclass(type(args[i]), ECPoint):
            y = args[i].normalize().p if len(args[i].p) == 3 else args[i].p
            b += serialize(*y)
        elif issubclass(type(args[i]), FQ2) or issubclass(type(args[i]), optimized_FQ2):
            b += serialize(*args[i].coeffs)
        elif type(args[i]) is str:
            b += args[i].encode('utf-8')
        elif type(args[i]) is bytes:
            b += args[i]
        elif issubclass(type(args[i]), py_ecc_FQ): # TODO: remove
            b += serialize(args[i].n)
        elif type(args[i]) is tuple:
            if len(args[i]) == 3 and all(map(lambda x: isinstance(x, optimized_bn128_FQ), args[i])):
                b += serialize(*normalize(args[i]))
            else:
                b += serialize(*args[i])
        elif type(args[i]) is list:
            b += serialize(*args[i])
        else:
            #import inspect
            #print(inspect.getmro(args[i].__class__))
            raise SerializationError(f'Cannot serialize argument of type {type(args[i])}')

    return b

def int_tuple_to_point(i, j):
    return (i << MAX_INT_SIZE*8) | j

def initialize_2d_array(rows, columns):
    return [[None]*columns for _ in range(rows)]

def initialize_2d_arrays(rows, columns, count):
    return [initialize_2d_array(rows, columns) for _ in range(count)]

def multi_controller(P0, Ps):
    Pgs = [P() for P in Ps]
    for p in Pgs:
        next(p)

    p0 = P0(Pgs)
    value = next(p0)

    while True:
        try:
            value = next(p0)
        except StopIteration:
            return value

def controller(P1, P2):
    p1 = P1()
    value = next(p1)
    p2 = P2(value)
    value = next(p2)
    while True:
        try:
            value = p1.send(value)
            value = p2.send(value)
        except StopIteration:
            return value

def count_bytes(data): # TODO: (data, max_int_size=32)
    if data is None:
        return 0
    return len(serialize(data))

def byte_count_decorator(generator_func):
    def wrapper(*args, **kwargs):
        byte_counts = {'sent': 0, 'received': 0}
        gen = generator_func(*args, **kwargs)
        value = None
        while True:
            try:
                # send value to generator and get next value
                next_value = gen.send(value)
                byte_counts['sent'] += count_bytes(next_value)
                # send value back to the caller
                value = yield next_value
                # TODO: pass max_int_size to count_bytes
                byte_counts['received'] += count_bytes(value)
            except GeneratorExit:
                print(f"func: '{generator_func.__name__}' sent {byte_counts['sent']} & received {byte_counts['received']} bytes")
                break
            except StopIteration:
                break
    return wrapper

from functools import wraps
from time import time
def timing_decorator(f): # TODO: rename
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        #print('func: %r args:[%r, %r] took: %2.4f sec' % (f.__name__, args, kw, te-ts))
        print('func: %r took: %2.4f sec' % (f.__name__, te - ts))
        return result

    return wrap
