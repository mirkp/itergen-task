from lark import Lark
from lark.exceptions import UnexpectedInput

parser = Lark.open("json_format.lark", parser="lalr")

test_string = 'a'

try:
    tree = parser.parse(test_string)
    print("Valid according to grammar")
    print(tree.pretty())
except UnexpectedInput as e:
    print("Invalid according to grammar")
    print(e)
