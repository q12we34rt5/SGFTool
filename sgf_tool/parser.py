from .lexer import SGFLexer, SGFToken, SGFTokenType
from .node import SGFNode
from .exceptions import SGFError
import typing


class NodeAllocator:
    def allocate(self) -> SGFNode:
        return SGFNode()


class SGFParser:
    class __DummyNode(SGFNode):
        def __init__(self):
            super().__init__()

        def get_child(self, index):
            return super().get_child(index)

        def add_child(self, child):
            if self.child is not None:
                raise RuntimeError('Dummy node cannot have more than one child')
            self.child = child

    def __init__(self, node_allocator: NodeAllocator = NodeAllocator()):
        self.node_allocator = node_allocator

    def parse(self, sgf: str, start: int = 0, progress_callback: typing.Optional[typing.Callable[[int, int], None]] = None) -> typing.Optional[SGFNode]:
        iterator = self.parse_iterator(sgf, start, progress_callback)
        root = next(iterator, None)
        for _ in iterator:
            pass
        return root

    def parse_iterator(self, sgf: str, start: int = 0, progress_callback: typing.Optional[typing.Callable[[int, int], None]] = None) -> typing.Generator[SGFNode, None, None]:
        lexer = SGFLexer(sgf, start, progress_callback)
        root = self.__DummyNode()  # dummy root
        current = root
        stack = []

        # cache data
        # cache_tag = None
        cache_values = None  # ['DUMMY_VALUE']

        # states
        next_can_be_left_paren = True
        next_can_be_right_paren = False
        next_can_be_semicolon = False
        next_can_be_tag = False
        next_can_be_value = False

        while True:
            token = lexer.next_token()
            if token is None:
                break

            if token.type == SGFTokenType.LEFT_PAREN:
                if not next_can_be_left_paren:
                    raise SGFError('Unexpected left parentheses', token.start, token.end, detail=True, sgf=sgf)

                stack.append(current)
                stack.append(token)  # append '(' token to stack

                # update states
                next_can_be_left_paren = False
                next_can_be_right_paren = False
                next_can_be_semicolon = True
                next_can_be_tag = False
                next_can_be_value = False

            elif token.type == SGFTokenType.RIGHT_PAREN:
                if not next_can_be_right_paren:
                    raise SGFError('Unexpected right parentheses', token.start, token.end, detail=True, sgf=sgf)

                if len(stack) == 0:
                    raise SGFError('Unmatched right parentheses', token.start, token.end, detail=True, sgf=sgf)

                # store tag and value to current node if needed
                if cache_values is not None:
                    current[cache_tag] = cache_values
                    cache_values = None
                    yield current

                # pop until '('
                while True:
                    if len(stack) == 0:
                        raise SGFError('Unmatched right parentheses', token.start, token.end, detail=True, sgf=sgf)
                    # check stack[-1] is a token first
                    if isinstance(stack[-1], SGFToken) and stack[-1].type == SGFTokenType.LEFT_PAREN:
                        stack.pop()  # pop '(' token
                        break
                    stack.pop()  # pop node
                current = stack.pop()  # pop the node before '('

                # update states
                next_can_be_left_paren = True
                next_can_be_right_paren = True
                next_can_be_semicolon = False
                next_can_be_tag = False
                next_can_be_value = False

            elif token.type == SGFTokenType.SEMICOLON:
                if not next_can_be_semicolon:
                    raise SGFError('Unexpected semicolon', token.start, token.end, detail=True, sgf=sgf)

                # store tag and value to current node if needed
                if cache_values is not None:
                    current[cache_tag] = cache_values
                    cache_values = None
                    yield current

                # create a new node
                stack.append(current)
                current = self.node_allocator.allocate()
                stack[-1].add_child(current)

                # update states
                next_can_be_left_paren = False
                next_can_be_right_paren = False
                next_can_be_semicolon = False
                next_can_be_tag = True
                next_can_be_value = False

            elif token.type == SGFTokenType.TAG:
                if not next_can_be_tag:
                    raise SGFError(f'Unexpected tag {token.value}', token.start, token.end, detail=True, sgf=sgf)

                # store tag and value to current node if needed
                if cache_values is not None:
                    current[cache_tag] = cache_values
                    cache_values = None

                cache_tag = token.value  # cache the tag, will be used when the value comes

                # update states
                next_can_be_left_paren = False
                next_can_be_right_paren = False
                next_can_be_semicolon = False
                next_can_be_tag = False
                next_can_be_value = True

            elif token.type == SGFTokenType.VALUE or token.type == SGFTokenType.EMPTY_VALUE:
                if not next_can_be_value:
                    raise SGFError(f'Unexpected value {token.value}', token.start, token.end, detail=True, sgf=sgf)

                if cache_values is None:
                    cache_values = []
                value = token.value[1:-1]
                cache_values.append(value)

                # update states
                next_can_be_left_paren = True
                next_can_be_right_paren = True
                next_can_be_semicolon = True
                next_can_be_tag = True
                next_can_be_value = True

            elif token.type == SGFTokenType.IGNORE:
                pass
            else:
                raise SGFError(f'Invalid token {token.value}', token.start, token.end, detail=True, sgf=sgf)

        # make sure all the parentheses are matched
        if len(stack) > 0:
            # pop until the first '(' token
            while len(stack) > 0:
                if isinstance(stack[-1], SGFToken) and stack[-1].type == SGFTokenType.LEFT_PAREN:
                    last_left_paren = stack.pop()
                    break
                stack.pop()
            raise SGFError('Unmatched left parentheses', last_left_paren.start, last_left_paren.end, detail=True, sgf=sgf)

        # remove the dummy root
        root = root.get_child(0)
        if root:
            root.detach()
