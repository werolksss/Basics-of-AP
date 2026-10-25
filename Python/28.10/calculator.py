import importlib
import sys
from operations import IOperation


# Ядро получает готовые операции извне.
class Calculator:
    def __init__(self, operations):
        self.operations = operations

    def calculate(self, name, a, b):
        return self.operations[name].apply(a, b)


def load(spec):
    # Формат подключения: имя_модуля:имя_класса
    module, name = spec.split(":")
    operation = getattr(importlib.import_module(module), name)()
    if not isinstance(operation, IOperation):
        raise TypeError("Компонент должен реализовывать IOperation")
    return name, operation


if __name__ == "__main__":
    try:
        calculator = Calculator(dict(load(s) for s in sys.argv[1:]))
        print("Операции:", ", ".join(calculator.operations))

        while True:
            text = input("Операция a b или EXIT: ")
            if text.upper() == "EXIT":
                break
            try:
                name, a, b = text.split()
                print(calculator.calculate(name, float(a), float(b)))
            except (ValueError, KeyError, ArithmeticError) as error:
                print("Ошибка:", error)
    except (EOFError, KeyboardInterrupt):
        pass
