import enum
import re
from .exceptions import LexicalError


class SGFTokenType(enum.Enum):
    LEFT_PAREN = 0
    RIGHT_PAREN = 1
    SEMICOLON = 2
    TAG = 3
    EMPTY_VALUE = 4
    VALUE = 5
    IGNORE = 6


SGFTokenRules = [
    (SGFTokenType.LEFT_PAREN,  re.compile(r'\(')),
    (SGFTokenType.RIGHT_PAREN, re.compile(r'\)')),
    (SGFTokenType.SEMICOLON,   re.compile(r';')),
    (SGFTokenType.TAG,         re.compile(r'\w+')),
    (SGFTokenType.EMPTY_VALUE, re.compile(r'\[\]')),
    (SGFTokenType.VALUE,       re.compile(r'\[[\S\s]*?[^\\]\]')),
    (SGFTokenType.IGNORE,      re.compile(r'\s+')),
]


class SGFToken:
    def __init__(self, type: SGFTokenType, value: str, start: int, end: int):
        self.type = type
        self.value = value
        self.start = start
        self.end = end


class SGFLexer:
    def __init__(self, sgf: str, start: int = 0):
        self.sgf = sgf
        self.index = start
        self.length = len(sgf)

    def next_token(self):
        if self.index >= self.length:
            return None

        for token_type, pattern in SGFTokenRules:
            match = pattern.match(self.sgf, self.index)
            if match:
                value = match.group(0)
                token = SGFToken(token_type, value, self.index, self.index + len(value))
                self.index = token.end
                return token

        raise LexicalError(f'Invalid character \'{self.sgf[self.index]}\' at {self.index}')
