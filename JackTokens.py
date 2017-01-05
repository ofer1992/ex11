from enum import Enum

KEYWORDS = {'class', 'constructor', 'function', 'method', 'field', 'static',
            'var', 'int', 'char', 'boolean',
            'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else',
            'while', 'return'}
SYMBOLS = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/',
           '&', '|',
           '<', '>', '=', '-', '~'}
OPERATORS = {'+', '-', '*', '/', '&', '|',
             '<', '>', '='}


class JackTokens(Enum):
    """

    """
    ERROR = -1
    KEYWORD = 0
    SYMBOL = 1
    IDENTIFIER = 2
    INT_CONST = 3
    STRING_CONST = 4