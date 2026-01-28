from lark import Lark
from lark.exceptions import UnexpectedInput

parser = Lark.open("tool_call.lark", parser="lalr")

test_string = '{"name": "test tool", "args": { "item" : [1, 2, 3], "": { }} }'

try:
    tree = parser.parse(test_string)
    print("Valid according to grammar")
    print(tree.pretty())
except UnexpectedInput as e:
    print("Invalid according to grammar")
    print(e)
