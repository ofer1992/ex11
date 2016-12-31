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

    CLASS = 5
    METHOD = 6
    FUNCTION = 7
    CONSTRUCTOR = 8
    INT = 9
    BOOLEAN = 10
    CHAR = 11
    VOID = 12
    VAR = 13
    STATIC = 14
    FIELD = 15
    LET = 16
    DO = 17
    IF = 18
    ELSE = 19
    WHILE = 20
    RETURN = 21
    TRUE = 22
    FALSE = 23
    NULL = 24
    THIS = 25