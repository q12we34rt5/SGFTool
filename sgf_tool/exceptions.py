class LexicalError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class SGFError(Exception):
    def __init__(self, message, start, end, detail=False, sgf=None, offset=20, highlight='\033[1;31m'):
        self.message = message
        self.start = start
        self.end = end
        self.detail = detail
        self.sgf = sgf
        self.offset = offset
        self.highlight = highlight

    def __str__(self):
        if not self.detail:
            return f'{self.message} at {self.start}:{self.end}'
        else:
            if self.sgf is None:
                return f'{self.message} at {self.start}:{self.end}'
            s = max(0, self.start - self.offset)
            e = min(len(self.sgf), self.end + self.offset)
            return f'{self.message} at {self.start}:{self.end}\n{self.sgf[s:self.start]}{self.highlight}{self.sgf[self.start:self.end]}\033[0m{self.sgf[self.end:e]}'
