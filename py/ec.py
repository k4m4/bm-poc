from functools import reduce
from importlib import import_module
from secrets import randbelow
from typing import Self, List, Union
from abc import ABC, abstractmethod
from py_ecc.typing import Point2D, Field

class FQ(ABC):
    def __init__(self: Self, n: int):
        self.n = n

    def __add__(self: Self, other: Self) -> Self:
        return self.__class__((self.n + other.n) % self.curve_order())

    def __sub__(self: Self, other: Self) -> Self:
        return self.__class__((self.n - other.n) % self.curve_order())

    def __mul__(self: Self, other: Self) -> Self:
        return self.__class__((self.n * other.n) % self.curve_order())

    def __pow__(self: Self, exp: int) -> Self:
        return self.__class__(pow(self.n, exp, self.curve_order()))

    def __repr__(self: Self) -> str:
        return f'{self.__class__.__name__}({self.n})'

    def __eq__(self: Self, other: Union[Self, int]) -> bool:
        if isinstance(other, int):
            return self.n == other

        return self.n == other.n

    @classmethod
    @abstractmethod
    def curve_order(cls) -> int:
        pass

    @classmethod
    def rand(cls):
        return cls(randbelow(cls.curve_order()))

    @classmethod
    def sum(cls, fqs: List['FQ']):
        assert fqs
        return reduce(lambda a, b: a + b, fqs)

class ECPoint(ABC):
    def __init__(self, p: Point2D[Field]):
        self.p = p

    @classmethod
    @abstractmethod
    def G1(cls):
        pass

    @classmethod
    @abstractmethod
    def G2(cls):
        pass

    def __radd__(self, other: Self):
        return self.__add__(other)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{self.p.__repr__()}"

    @abstractmethod
    def __mul__(self, fq: FQ): # TODO: just int instead of FQ
        pass

    @abstractmethod
    def __add__(self, other: Self):
        pass

    @abstractmethod
    def normalize(self):
        pass

    @abstractmethod
    def neg(self):
        pass

    @classmethod
    def pairing(cls, p1: Self, p2: Self):
        pass

    def __eq__(self, other: Self) -> bool:
        return self.normalize().p == other.normalize().p

    @classmethod
    def sum(cls, fqs: list[FQ]):
        assert fqs
        return reduce(lambda x, y: x + y, fqs)

def create_fq(name, curve_order):
    class ThisFQ(FQ):
        @classmethod
        def curve_order(cls) -> int:
            return curve_order

    ThisFQ.__name__ = name

    return ThisFQ

def create_curve(name, fq: FQ, G1, G2, add, mul, norm, neg, pairing):
    class ThisCurve(ECPoint):
        @classmethod
        def G1(cls):
            return cls(G1)

        @classmethod
        def G2(cls):
            return cls(G2)

        def __mul__(self, fq: FQ):
            return self.__class__(mul(self.p, fq.n))

        def __add__(self, other: Self):
            return self.__class__(add(self.p, other.p))

        def normalize(self):
            return self.__class__(norm(self.p))

        def neg(self):
            return self.__class__(neg(self.p))

        @classmethod
        def pairing(cls, *ps): # TODO: should return FQ12
            return pairing(*[p.p for p in ps])

    ThisCurve.__name__ = name

    return ThisCurve

def from_ecc_py(name, module):
    ThisFQ = create_fq(f'{name}FQ', module.curve_order)
    ThisCurve = create_curve(f'{name}Point', ThisFQ, module.G1, module.G2, module.add, module.multiply, module.normalize if hasattr(module, 'normalize') else lambda x: x, module.neg, module.pairing)
    return ThisFQ, ThisCurve
