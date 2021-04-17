"""CSC111 Winter 2021 Project - vertex_graph.py

PLEASE REFER TO THE [COMPUTATIONAL OVERVIEW] SECTION IN THE REPORT BEFORE READING DOCSTRINGS!

OBJECTIVE: Define the classes _WeightedVertex and WeightedGraph for use in pathfinding.
Define the function nested_list_to_graph for converting a list-based representation of the game map
into a graph-based one.

The implementations for _WeightedVertex and WeightedGraph were copied over from CSC111 Assignment 3.
Minor modifications were made such as removing ValueError returns for certain methods.

The function nested_list_to_graph is original work.

This file is Copyright (c)
2021 David Liu and Isaac Waller,
2021 Hyun Jo (Joshua) Jang."""

from __future__ import annotations
from typing import Any, Union, Dict, Tuple


class _WeightedVertex:
    """
    Instance Attributes:
        - item: The data stored in this vertex, representing a user or book.
        - neighbours: The vertices that are adjacent to this vertex, and their corresponding
            edge weights.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
    """
    item: Any
    neighbours: dict[_WeightedVertex, Union[int, float]]  # NOW A DICTIONARY!!!!!!

    def __init__(self, item: Any) -> None:
        """Initialize a new vertex with the given item.

        This vertex is initialized with no neighbours.
        """
        self.item = item
        self.neighbours = {}

    def check_connected(self, target_item: Any, visited: set[_WeightedVertex]) -> bool:
        """Return whether this vertex is connected to a vertex corresponding to the target_item,
        WITHOUT using any of the vertices in visited.

        Preconditions:
            - self not in visited
        """
        if self.item == target_item:
            # Our base case: the target_item is the current vertex
            return True
        else:
            visited.add(self)  # Add self to the set of visited vertices
            for u in self.neighbours:
                if u not in visited:  # Only recurse on vertices that haven't been visited
                    if u.check_connected(target_item, visited):
                        return True

            return False


class WeightedGraph:
    """A weighted graph used to represent the grid representation of the 16x9 tile map.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _WeightedVertex object.
    _vertices: dict[Any, _WeightedVertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any) -> None:
        """Add a vertex with the given item and kind to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.
        """
        if item not in self._vertices:
            self._vertices[item] = _WeightedVertex(item)

    def add_edge(self, item1: Any, item2: Any, weight: Union[int, float] = 1) -> None:
        """Add an edge between the two vertices with the given items in this graph,
        with the given weight.

        Do nothing if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            # Add the new edge
            v1.neighbours[v2] = weight
            v2.neighbours[v1] = weight

    def get_weight(self, item1: Any, item2: Any) -> Union[int, float]:
        """Return the weight of the edge between the given items.

        Return 0 if item1 and item2 are not adjacent.

        Preconditions:
            - item1 and item2 are vertices in this graph
        """
        v1 = self._vertices[item1]
        v2 = self._vertices[item2]
        return v1.neighbours.get(v2, 0)

    def get_neighbours(self, item: Any) -> set:
        """Return a set of the neighbours of the given item.

        Note that the *items* are returned, not the _Vertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour.item for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_all_vertices(self) -> set:
        """Return a set of all vertex items in this graph.
        """
        return set(self._vertices.keys())

    def connected(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are connected vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        """

        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return v1.check_connected(item2, set())  # Pass in an empty "visited" set
        else:
            return False


def dict_to_graph(representation: Dict[Tuple[int, int], str]) -> WeightedGraph:
    """Take a dictionary representation of the game map and convert it into a WeightedGraph.

    The dictionary representation returns tile type: 'obstacle', 'normal', 'slow', 'goal'
    when given a grid location tuple.

    Different tile types result in different weights of edges connecting them.
    A normal-normal edge will have weight 1 + 1 = 2, A normal-slow edge will have 1 + 5 = 6, etc.

    Obstacle tiles are treated as non-tiles; i.e. no vertices will be made for them.

    This implies that blocked off path <=> start and goal locations are not connected
    """
    DIMENSION = (16, 9)

    graph = WeightedGraph()
    type_to_weight = {'normal': 1, 'slow': 5, 'goal': 1, 'obstacle': 0}  # dict for weights

    # First, add vertices.
    for location in representation:
        if representation[location] != 'obstacle':
            graph.add_vertex(location)

    # Connect all vertices with adjacent ones.
    for i in range(DIMENSION[0]):
        for j in range(DIMENSION[1]):
            v0 = (i, j)
            v1 = (i + 1, j)  # vertex to the right
            v2 = (i, j + 1)  # vertex below

            if v0 in representation and v1 in representation:  # Avoid keyerror
                # If either v0 or v1 is an obstacle,
                # the edge will not be added since there will be no corresponding vertex.
                graph.add_edge(
                    v0, v1, type_to_weight[representation[v0]] + type_to_weight[representation[v1]])

            if v0 in representation and v2 in representation:
                graph.add_edge(
                    v0, v2, type_to_weight[representation[v0]] + type_to_weight[representation[v2]])

    return graph


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 100,
        'disable': ['E1136'],
        'extra-imports': [],
        'allowed-io': [],
        'max-nested-blocks': 4
    })
