"""CSC111 Winter 2021 Project - pathfinding.py

PLEASE REFER TO THE [COMPUTATIONAL OVERVIEW] SECTION IN THE REPORT BEFORE READING DOCSTRINGS!

OBJECTIVE: Define functions responsible for finding the shortest path between two locations,
given a WeightedGraph representation of the 16x9 map.

The meat and bones of this project.

This file is Copyright (c) 2021 Hyun Jo (Joshua) Jang."""

from typing import Tuple, List, Dict, Union
from heapq import heappush, heappop
import math
import vertex_graph as vg


def a_star_pathfinding(graph_representation: vg.WeightedGraph, start_loc: Tuple[int, int],
                       is_dstra: bool = False) -> List[Tuple[int, int]]:
    """Perform an A* path search on the given graph.
    The search is done on start_loc to GOAL_LOC as endpoints.

    Return a list of locations which make up the final shortest path,
    including the start and goal locations.

    When is_dstra == True, do not account for the heuristic function when calculating scores.
    This allows for the emulation of Dijkstra's Algorithm within the A* function.

    The Wikipedia Article for the A* Search Algorithm was referred to during the implementation of
    this function.

    Preconditions:
        - start_loc in graph_representation.get_all_vertices()
    """
    # Goal location is always (15, 4)
    GOAL_LOC = (15, 4)

    priorityq = []  # Our priority queue to be used in A*.
    heappush(priorityq, (0, start_loc))

    came_from = {start_loc: None}
    cost_to_loc = {start_loc: 0}

    while len(priorityq) != 0:  # While priority queue is not empty
        current_loc = heappop(priorityq)[1]  # Pick the topmost location in the priority queue

        if current_loc == GOAL_LOC:  # When the topmost location in the priority queue,
            return _reconstruct_path(came_from, GOAL_LOC)  # We can safely terminate.

        # Expand into neighbours
        for neighbour_loc in graph_representation.get_neighbours(current_loc):
            # Calculate cost to neighbour (without heuristic value)
            # using currently known smallest cost
            cost = cost_to_loc[current_loc] + graph_representation.get_weight(current_loc,
                                                                              neighbour_loc)

            if (neighbour_loc not in cost_to_loc) or (cost < cost_to_loc[neighbour_loc]):
                # If cost from start to neighbour loc is infinity (not in cost_to_loc),
                # or this path to neighbour_loc is better than any previous non-infinity path

                # Update cost and came_from info for that neighbour_loc.
                cost_to_loc[neighbour_loc] = cost
                came_from[neighbour_loc] = current_loc

                # Calculate new score (cost + heuristic value) for neighbour_loc
                score = cost
                if not is_dstra:
                    score += _heuristic(neighbour_loc)  # For Dijkstra's Algorithm, heuristic(x) = 0

                heappush(priorityq, (score, neighbour_loc))  # Push into priority queue.


def _heuristic(loc: Tuple[int]) -> float:
    """Return the Euclidian distance from a given location to GOAL_LOC.

    In theory, the heuristic function for A* can be any consistent function which estimates
    the direction/distance from any given point to the goal.
    In our situation, Euclidian distance is good enough.
    """
    # Use Pythagorean theorem to calculate Euclidian distance
    GOAL_LOC = (15, 4)
    return math.sqrt(math.pow((GOAL_LOC[0] - loc[0]), 2) + math.pow((GOAL_LOC[1] - loc[1]), 2))


def _reconstruct_path(came_from: Dict[Tuple[int, int], Union[None, Tuple[int, int]]],
                      current_loc: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Return the full path (list of locations) from start to goal (current_loc),
    using came_from as a reference.

    This is simply looking at the fastest location to current_loc,
    then looking at the fastest location to that location, and so on.
    """
    GOAL_LOC = (15, 4)
    full_path = []

    while current_loc in came_from:
        current_loc = came_from[current_loc]
        full_path.append(current_loc)

    full_path.remove(None)
    full_path.reverse()
    full_path.append(GOAL_LOC)
    return full_path


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 100,
        'disable': ['E1136'],
        'extra-imports': ['vertex_graph', 'math', 'heapq'],
        'allowed-io': [],
        'max-nested-blocks': 4
    })
