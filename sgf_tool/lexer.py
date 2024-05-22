import enum
import re
from .exceptions import LexicalError
import typing


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
    def __init__(self, sgf: str, start: int = 0, progress_callback: typing.Optional[typing.Callable[[int, int], None]] = None):
        self.sgf = sgf
        self.index = start
        self.length = len(sgf)
        self.progress_callback = progress_callback

    def next_token(self):
        if self.index >= self.length:
            return None

        for token_type, pattern in SGFTokenRules:
            match = pattern.match(self.sgf, self.index)
            if match:
                value = match.group(0)
                token = SGFToken(token_type, value, self.index, self.index + len(value))
                self.index = token.end

                # track progress
                if self.progress_callback:
                    self.progress_callback(self.index, self.length)

                return token

        raise LexicalError('Invalid character', self.index, self.index + 1, detail=True, sgf=self.sgf)
