import abc
from collections import OrderedDict
import typing


class BaseSGFNode(abc.ABC):
    @abc.abstractmethod
    def __setitem__(self, key, value):
        pass

    @abc.abstractmethod
    def __getitem__(self, key):
        pass

    @abc.abstractmethod
    def __contains__(self, key):
        pass

    @abc.abstractmethod
    def __str__(self):
        pass

    @abc.abstractmethod
    def to_sgf(self):
        """
        Convert the node to an SGF string.
        """
        pass

    @abc.abstractmethod
    def get_tags(self):
        """
        Get all the tags in the node.
        """
        pass

    @abc.abstractmethod
    def get_parent(self):
        """
        Get the parent node of the node.
        """
        pass

    @abc.abstractmethod
    def get_child(self, index):
        """
        Get the child node at the specified index.
        """
        pass

    @abc.abstractmethod
    def get_num_children(self):
        """
        Get the number of children.
        """
        pass

    @abc.abstractmethod
    def add_child(self, child):
        """
        Add a child node to the node.
        """
        pass

    @abc.abstractmethod
    def detach(self):
        """
        Detach the node from the tree and return the node itself.
        """
        pass

    def get_children_iter(self):
        """
        Get an iterator of the children.

        Warning: If any operation is performed that changes the children, the iterator probably becomes invalid.
        """
        # Warning:
        #   This method is not abstract, but it is highly recommended to override it.
        #   By default, it uses get_child() to get the children, which is not efficient.
        for i in range(self.get_num_children()):
            yield self.get_child(i)


class SGFNode(BaseSGFNode):
    def __init__(self):
        self.parent: typing.Optional[SGFNode] = None
        self.child: typing.Optional[SGFNode] = None
        self.next_sibling: typing.Optional[SGFNode] = None
        self.num_children: int = 0
        self.properties: OrderedDict[str, list[str]] = OrderedDict()

    def __setitem__(self, key, value):
        if not hasattr(value, '__iter__') or isinstance(value, str):
            raise ValueError('Value must be an iterable object other than str.')
        self.properties[key] = list(value)

    def __getitem__(self, key):
        return self.properties[key]

    def __contains__(self, key):
        return key in self.properties

    def __str__(self):
        result = ';'
        for key, value in self.properties.items():
            result += f'{key}[{"][".join(value)}]'
        return result

    def to_sgf(self):
        result = str(self)
        if self.child:
            result += self.child.to_sgf()
        if self.next_sibling:
            if self.next_sibling.next_sibling:
                result = '(' + result + ')' + self.next_sibling.to_sgf()
            else:
                # Since the last sibling cannot be checked if it has siblings, we need to check it here
                result = '(' + result + ')(' + self.next_sibling.to_sgf() + ')'
        return result

    def get_tags(self):
        return self.properties.keys()

    def get_parent(self):
        return self.parent

    def get_child(self, index):
        ptr = self.child
        for _ in range(index):
            if ptr is None:
                return None
            ptr = ptr.next_sibling
        return ptr

    def get_num_children(self):
        return self.num_children

    def add_child(self, child):
        child.detach()
        if self.child is None:
            self.child = child
        else:
            ptr = self.child
            while ptr.next_sibling:
                ptr = ptr.next_sibling
            ptr.next_sibling = child
        child.parent = self
        self.num_children += 1

    def detach(self):
        if self.parent:
            if self.parent.child == self:
                self.parent.child = self.next_sibling
            else:
                ptr = self.parent.child
                while ptr.next_sibling != self:
                    ptr = ptr.next_sibling
                ptr.next_sibling = self.next_sibling
            self.parent.num_children -= 1
            self.parent = None
            self.next_sibling = None
        return self

    def get_children_iter(self):
        ptr = self.child
        while ptr:
            yield ptr
            ptr = ptr.next_sibling
