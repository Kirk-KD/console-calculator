import ast
import operator

OP_LOOKUP = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,      # Note: power in math exp uses ^ instead of ** in python
    ast.UAdd: operator.pos,
    ast.USub: operator.neg
}


def _eval(node):
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        return OP_LOOKUP[type(node.op)](_eval(node.left), _eval(node.right))
    elif isinstance(node, ast.UnaryOp):
        return OP_LOOKUP[type(node.op)](_eval(node.operand))
    else:
        raise TypeError(node)


def unparse(node):
    return ast.unparse(node).replace("**", "^")


def eval_math(expr: str, do_unparse: bool=True):
    node = ast.parse(expr.replace("^", "**"), mode="eval").body
    return _eval(node), (unparse(node) if do_unparse else None)
