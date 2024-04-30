from hash_to_field import Hp
from py_ecc.utils import prime_field_inv as inv
from py_ecc.bn128 import (
    field_modulus as FIELD_MODULUS,
    FQ, add, b, neg
)

def hash_to_point(msg, dst):
    [e0], [e1] = Hp(msg, 2, dst)
    p0 = map_to_point(e0)
    p1 = map_to_point(e1)
    p = add(p0, p1)
    return p

def sqrt(x: FQ):
    x0 = x**((FIELD_MODULUS+1)//4)
    if (x == x0**2):
        return x0
    else:
        return FQ.zero()

def get_xy1(x_1, x_2, x_3):
    # Check x_1
    y2 = x_1**3 + b
    y = sqrt(y2)

    if (y != FQ.zero()):
        return (x_1, y)

    # Check x_2
    y2 = x_2**3 + b
    y = sqrt(y2)

    if (y != FQ.zero()):
        return (x_2, y)

    # Check x_3
    y2 = x_3**3 + b
    y = sqrt(y2)
    assert(y != FQ.zero())
    return (x_3, y)

# https://www.di.ens.fr/~fouque/pub/latincrypt12.pdf
def map_to_point(t):
    if type(t) != FQ:
        t = FQ(t)

    x = sqrt(t)
    decision = x*x == t # TODO: check

    sqrt3 = sqrt(FQ(-3))
    F0 = ((sqrt3-1)/2, sqrt(1+b))

    if t == 0:
        return F0 # TODO: check

    w = sqrt3*t/(1+b+t**2)
    x_1 = (sqrt3-1)/2 - t*w
    x_2 = -x_1 - 1
    x_3 = 1 + 1 / w**2

    T = get_xy1(x_1, x_2, x_3)

    ret = T
    #ret = add(F0, T) # TODO: check

    if not decision: # TODO: check
        ret = neg(ret)

    return ret
