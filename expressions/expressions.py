from functools import singledispatch
import numbers


class Expression:
    def __init__(self, *operands) -> None:
        self.operands = operands

    def __add__(self, other):
        if isinstance(other, Expression):
            return Add(self, other)
        elif isinstance(other, numbers.Number):
            return Add(self, Number(other))
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, Expression):
            return Add(other, self)
        elif isinstance(other, numbers.Number):
            return Add(Number(other), self)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Expression):
            return Sub(self, other)
        elif isinstance(other, numbers.Number):
            return Sub(self, Number(other))
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, Expression):
            return Sub(other, self)
        elif isinstance(other, numbers.Number):
            return Sub(Number(other), self)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, Expression):
            return Mul(self, other)
        elif isinstance(other, numbers.Number):
            return Mul(self, Number(other))
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, Expression):
            return Mul(other, self)
        elif isinstance(other, numbers.Number):
            return Mul(Number(other), self)
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, Expression):
            return Div(self, other)
        elif isinstance(other, numbers.Number):
            return Div(self, Number(other))
        return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, Expression):
            return Div(other, self)
        elif isinstance(other, numbers.Number):
            return Div(Number(other), self)
        return NotImplemented

    def __pow__(self, other):
        if isinstance(other, Expression):
            return Pow(self, other)
        elif isinstance(other, numbers.Number):
            return Pow(self, Number(other))
        return NotImplemented

    def __rpow__(self, other):
        if isinstance(other, Expression):
            return Pow(other, self)
        elif isinstance(other, numbers.Number):
            return Pow(Number(other), self)
        return NotImplemented


class Operator(Expression):
    def __repr__(self) -> str:
        return type(self).__name__ + repr(self.operands)

    def __str__(self) -> str:
        def parentheses(operand):
            if operand.precedence < self.precedence:
                return f"({str(operand)})"
            return str(operand)

        return f" {self.symbol} ".join((map(parentheses, self.operands)))


class Add(Operator):
    precedence = 0
    symbol = "+"


class Sub(Operator):
    precedence = 0
    symbol = "-"


class Mul(Operator):
    precedence = 1
    symbol = "*"


class Div(Operator):
    precedence = 1
    symbol = "/"


class Pow(Operator):
    precedence = 2
    symbol = "^"


class Terminal(Expression):
    precedence = 3

    def __init__(self, value):
        self.value = value
        super().__init__()

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)


class Number(Terminal):
    def __init__(self, value):
        if not isinstance(value, numbers.Number):
            raise TypeError("Value passed to Number should be a number.")
        super().__init__(value)


class Symbol(Terminal):
    def __init__(self, value):
        if not isinstance(value, str):
            raise TypeError("Value passed to Symbol should be a string.")
        super().__init__(value)


def postvisitor(expr: Expression, fn, **kwargs):
    stack = []
    visited = {}
    stack.append(expr)
    while stack:
        e = stack.pop()
        unvisited_children = []
        for o in e.operands:
            if o not in visited:
                unvisited_children.append(o)
        if unvisited_children:
            stack.append(e)
            stack.extend(unvisited_children)
        else:
            visited[e] = fn(e, *(visited[o] for o in e.operands), **kwargs)
    return visited[expr]


@singledispatch
def differentiate(expr: Expression, *o, **kwargs):
    raise NotImplementedError(f"Cannot differentiate {type(expr).__name__}")


@differentiate.register(Number)
def _(expr, *o, **kwargs):
    return 0.0


@differentiate.register(Symbol)
def _(expr, *o, var, **kwargs):
    return 1.0 if expr.value == var else 0.0


@differentiate.register(Add)
def _(expr, *o, **kwargs):
    return o[0] + o[1]


@differentiate.register(Mul)
def _(expr, *o, **kwargs):
    return (o[0] * expr.operands[1]) + (o[1] * expr.operands[0])


@differentiate.register(Div)
def _(expr, *o, **kwargs):
    return ((o[0] * expr.operands[1]) - (expr.operands[0] * o[1])) \
            / (expr.operands[1] ** 2)


@differentiate.register(Pow)
def _(expr, *o, **kwargs):
    return o[0] * expr.operands[1] \
           * (expr.operands[0] ** (expr.operands[1] - 1))
