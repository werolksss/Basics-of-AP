from abc import ABC, abstractmethod


class IOperation(ABC):
    @abstractmethod
    def apply(self, a, b):
        pass


class Add(IOperation):
    def apply(self, a, b):
        return a + b


class Sub(IOperation):
    def apply(self, a, b):
        return a - b


class Mul(IOperation):
    def apply(self, a, b):
        return a * b


class Div(IOperation):
    def apply(self, a, b):
        if b == 0:
            raise ZeroDivisionError("Деление на ноль")
        return a / b
