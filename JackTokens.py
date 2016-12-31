from enum import Enum


class JackTokens(Enum):
    """

    """
    ERROR = -1
    KEYWORD = 0
    SYMBOL = 1
    IDENTIFIER = 2
    INT_CONST = 3
    STRING_CONST = 4