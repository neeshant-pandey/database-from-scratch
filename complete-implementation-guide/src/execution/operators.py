"""
Query execution operators using the iterator/volcano model.
"""

from abc import ABC, abstractmethod
from typing import Optional, Iterator, List, Tuple, Any
from ..storage.table_heap import TableHeap
from ..index.bptree import BPTreeIndex
from ..common.types import RID


class Operator(ABC):
    """
    Base class for all execution operators.
    Implements the iterator/volcano model.
    """

    @abstractmethod
    def init(self) -> None:
        """Initialize the operator."""
        pass

    @abstractmethod
    def next(self) -> Optional[Tuple]:
        """Get next tuple. Returns None when exhausted."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Cleanup resources."""
        pass

    def __iter__(self) -> Iterator[Tuple]:
        """Make operator iterable."""
        self.init()
        while True:
            tuple_data = self.next()
            if tuple_data is None:
                break
            yield tuple_data
        self.close()


class SeqScanOperator(Operator):
    """
    Sequential scan operator: reads all tuples from a table.
    """

    def __init__(self, table_heap: TableHeap):
        self.table_heap = table_heap
        self.iterator = None

    def init(self) -> None:
        self.iterator = self.table_heap.scan()

    def next(self) -> Optional[Tuple]:
        if self.iterator is None:
            return None

        try:
            rid, tuple_data = next(self.iterator)
            # Deserialize tuple_data here (simplified: just return bytes)
            return tuple_data
        except StopIteration:
            return None

    def close(self) -> None:
        self.iterator = None


class IndexScanOperator(Operator):
    """
    Index scan operator: uses B+ tree index for point or range queries.
    """

    def __init__(self, index: BPTreeIndex, table_heap: TableHeap,
                 start_key: int, end_key: Optional[int] = None):
        self.index = index
        self.table_heap = table_heap
        self.start_key = start_key
        self.end_key = end_key if end_key is not None else start_key
        self.iterator = None

    def init(self) -> None:
        self.iterator = self.index.range_scan(self.start_key, self.end_key)

    def next(self) -> Optional[Tuple]:
        if self.iterator is None:
            return None

        try:
            key, rid = next(self.iterator)
            # Fetch tuple from table
            tuple_data = self.table_heap.get_tuple(rid)
            return tuple_data
        except StopIteration:
            return None

    def close(self) -> None:
        self.iterator = None


class FilterOperator(Operator):
    """
    Filter operator: applies predicate to child operator's output.
    """

    def __init__(self, child: Operator, predicate):
        self.child = child
        self.predicate = predicate  # Function: tuple -> bool

    def init(self) -> None:
        self.child.init()

    def next(self) -> Optional[Tuple]:
        while True:
            tuple_data = self.child.next()
            if tuple_data is None:
                return None

            # Apply predicate
            if self.predicate(tuple_data):
                return tuple_data

    def close(self) -> None:
        self.child.close()


class ProjectionOperator(Operator):
    """
    Projection operator: selects specific columns from tuples.
    """

    def __init__(self, child: Operator, column_indices: List[int]):
        self.child = child
        self.column_indices = column_indices

    def init(self) -> None:
        self.child.init()

    def next(self) -> Optional[Tuple]:
        tuple_data = self.child.next()
        if tuple_data is None:
            return None

        # Project columns (simplified: assume tuple_data is list/tuple)
        # Real implementation would parse tuple format
        return tuple_data  # Placeholder

    def close(self) -> None:
        self.child.close()


class NestedLoopJoinOperator(Operator):
    """
    Nested loop join: for each outer tuple, scan all inner tuples.
    """

    def __init__(self, outer: Operator, inner: Operator, join_predicate):
        self.outer = outer
        self.inner = inner
        self.join_predicate = join_predicate  # Function: (outer_tuple, inner_tuple) -> bool
        self.current_outer = None

    def init(self) -> None:
        self.outer.init()
        self.inner.init()
        self.current_outer = self.outer.next()

    def next(self) -> Optional[Tuple]:
        while self.current_outer is not None:
            # Try to find matching inner tuple
            inner_tuple = self.inner.next()

            if inner_tuple is None:
                # Exhausted inner, move to next outer
                self.current_outer = self.outer.next()
                if self.current_outer is None:
                    return None

                # Reset inner
                self.inner.close()
                self.inner.init()
                continue

            # Check join predicate
            if self.join_predicate(self.current_outer, inner_tuple):
                # Return joined tuple
                return (self.current_outer, inner_tuple)

        return None

    def close(self) -> None:
        self.outer.close()
        self.inner.close()


class AggregationOperator(Operator):
    """
    Aggregation operator: computes aggregate functions (COUNT, SUM, AVG, etc.).
    """

    def __init__(self, child: Operator, group_by_columns: List[int],
                 agg_functions: List[str]):
        self.child = child
        self.group_by_columns = group_by_columns
        self.agg_functions = agg_functions  # ['COUNT', 'SUM', 'AVG', etc.]
        self.result_iterator = None

    def init(self) -> None:
        self.child.init()

        # Build hash table for grouping
        groups = {}
        for tuple_data in self.child:
            # Extract group key (simplified)
            group_key = tuple(tuple_data)  # Placeholder

            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(tuple_data)

        # Compute aggregates
        results = []
        for group_key, tuples in groups.items():
            # Compute aggregate functions
            agg_results = []
            for func in self.agg_functions:
                if func == 'COUNT':
                    agg_results.append(len(tuples))
                elif func == 'SUM':
                    # Simplified: sum first column
                    agg_results.append(sum(t[0] for t in tuples if isinstance(t, tuple)))
                # Add more aggregate functions...

            results.append((group_key, agg_results))

        self.result_iterator = iter(results)

    def next(self) -> Optional[Tuple]:
        if self.result_iterator is None:
            return None

        try:
            return next(self.result_iterator)
        except StopIteration:
            return None

    def close(self) -> None:
        self.child.close()
        self.result_iterator = None


class LimitOperator(Operator):
    """
    Limit operator: returns first N tuples.
    """

    def __init__(self, child: Operator, limit: int, offset: int = 0):
        self.child = child
        self.limit = limit
        self.offset = offset
        self.count = 0

    def init(self) -> None:
        self.child.init()
        self.count = 0

        # Skip offset tuples
        for _ in range(self.offset):
            if self.child.next() is None:
                break

    def next(self) -> Optional[Tuple]:
        if self.count >= self.limit:
            return None

        tuple_data = self.child.next()
        if tuple_data is not None:
            self.count += 1

        return tuple_data

    def close(self) -> None:
        self.child.close()
