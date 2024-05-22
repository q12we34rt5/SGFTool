from .node import BaseSGFNode
import typing
from collections import deque
import functools
import bisect


class Algorithm:
    @staticmethod
    def dfs(root: BaseSGFNode, visit_func: typing.Callable[[BaseSGFNode, int], None]):
        """
        Depth-first search on the tree.
        """
        Algorithm._dfs(root, visit_func, 0)

    @staticmethod
    def _dfs(root: BaseSGFNode, visit_func: typing.Callable[[BaseSGFNode, int], None], depth: int):
        visit_func(root, depth)
        for child in root.get_children_iter():
            Algorithm._dfs(child, visit_func, depth + 1)

    @staticmethod
    def bfs(root: BaseSGFNode, visit_func: typing.Callable[[BaseSGFNode, int], None]):
        """
        Breadth-first search on the tree.
        """
        queue = deque([(root, 0)])
        while len(queue) > 0:
            current, depth = queue.popleft()
            visit_func(current, depth)
            for child in current.get_children_iter():
                queue.append((child, depth + 1))

    @staticmethod
    def find_nodes_with_property(root: BaseSGFNode, tag: str, value: str, value_index: int = 0) -> typing.List[BaseSGFNode]:
        """
        Find nodes with a specific property.
        """
        results = []

        def visit_func(n, _):
            if tag in n:
                values = n[tag]
                if len(values) > value_index and values[value_index] == value:
                    results.append(n)

        Algorithm.dfs(root, visit_func)
        return results

    @staticmethod
    def binary_search(sorted_list, item, comparator):
        """
        Perform a binary search to find the index of an item in a sorted list using a comparator.
        Returns the index of the item if found, otherwise returns -1.
        """
        lo, hi = 0, len(sorted_list)
        while lo < hi:
            mid = (lo + hi) // 2
            cmp_result = comparator(sorted_list[mid], item)
            if cmp_result == 0:
                return mid
            elif cmp_result < 0:
                lo = mid + 1
            else:
                hi = mid
        return -1

    @staticmethod
    def bisect_left_with_comparator(sorted_list, item, comparator):
        """
        Perform a binary search to find the index of an item in a sorted list using a comparator.
        Returns the index of the item if found, otherwise returns -1.
        """
        class ComparatorWrapper:
            def __init__(self, item):
                self.item = item

            def __gt__(self, other):
                return comparator(self.item, other) > 0

        index = bisect.bisect_left(sorted_list, ComparatorWrapper(item))
        if index < len(sorted_list) and comparator(sorted_list[index], item) == 0:
            return index
        return -1

    @staticmethod
    def merge_tree(root: BaseSGFNode, other_root: BaseSGFNode, comparator: typing.Callable[[BaseSGFNode, BaseSGFNode], int], merge_func: typing.Callable[[BaseSGFNode, BaseSGFNode], BaseSGFNode]):
        """
        Merge two trees.

        comparator: (BaseSGFNode, BaseSGFNode) -> int
            Compare two nodes.
            Return 0 if they are equal.
            Return -1 if the first node is less than the second node.
            Return 1 if the first node is greater than the second node.

        merge_func: (BaseSGFNode, BaseSGFNode) -> BaseSGFNode
            Called when two nodes are equal.
            Return the merged node.
        """
        if comparator(root, other_root) != 0:
            raise ValueError("The two roots are not equal.")
        Algorithm._merge_tree(root, other_root, comparator, merge_func)

    @staticmethod
    def _merge_tree(root: BaseSGFNode, other_root: BaseSGFNode, comparator: typing.Callable[[BaseSGFNode, BaseSGFNode], int], merge_func: typing.Callable[[BaseSGFNode, BaseSGFNode], BaseSGFNode]):
        if merge_func is not None:
            merge_func(root, other_root)

        sorted_nodes = sorted(root.get_children_iter(), key=functools.cmp_to_key(comparator))
        # TODO: raise error if children have duplicates
        for child in list(other_root.get_children_iter()):
            index = Algorithm.bisect_left_with_comparator(sorted_nodes, child, comparator)
            if index != -1:
                Algorithm.merge_tree(sorted_nodes[index], child, comparator, merge_func)
            elif index == -1:
                root.add_child(child.detach())
