"""CSC111 Winter 2021 Project - gameobjects.py

PLEASE REFER TO THE [COMPUTATIONAL OVERVIEW] SECTION IN THE REPORT BEFORE READING DOCSTRINGS!

OBJECTIVE: Define Enemy and Tile classes for use in main.py.

This file is Copyright (c) 2021 Hyun Jo (Joshua) Jang.
"""
from typing import List, Tuple, Dict
import pygame
from tools import convert_loc_to_pos, convert_pos_to_loc


class Enemy(pygame.sprite.Sprite):
    """An enemy unit which can be deployed on the map.

    It follows its working_path (a list of locations/waypoints) every game loop update cycle.
    Its dimensions are 32x64 pixels (a single tile is 64x64).

    Instance Attributes:
        - image: The pygame.image object for this enemy
        - rect: The pygame.rect object tied to self.image
        - working_path: The path which this enemy unit will follow every frame.
                        Unlike the path variables used in main.py, this path is always changing
                        according to how much of the path this enemy unit has covered
        - start_loc: The grid location in which this enemy unit is deployed e.g. (4, 7)
        - grid: The list-based grid representation of the game map
                This is used for determining movement speed on certain tiles; e.g. slow tiles
        - x, y: The pixel position for the centre of this enemy unit.
    """

    image: pygame.image
    rect: pygame.rect

    working_path: List[Tuple[int, int]]

    start_loc: Tuple[int, int]
    grid: Dict[Tuple[int, int], str]

    x: int
    y: int

    def __init__(self, _path: List[Tuple[int, int]], _start_loc: Tuple[int, int],
                 _grid: Dict[Tuple[int, int], str]) -> None:
        """Initialise all instance attributes according to input.

        Preconditions:
            - _start_loc == _path[0]
        """
        pygame.sprite.Sprite.__init__(self)  # Initialise superclass

        self.image = pygame.image.load('assets/sprite_enemy.png').convert()  # Load sprite.
        self.rect = self.image.get_rect()

        # The first element in _path will be the currently deployed tile/location,
        # remove this first element.
        self.working_path = _path[1:]

        self.start_loc = _start_loc

        # Set this unit's on-screen position to be the centre of start_loc's tile.
        self.rect.left = convert_loc_to_pos(self.start_loc, 'topleft')[0] + 16  # + 16 is centering.
        self.rect.top = convert_loc_to_pos(self.start_loc, 'topleft')[1]

        self.grid = _grid

    def update(self) -> None:
        """Behaviour for each game loop update cycle.
        Move this enemy unit towards its next location/waypoint in self.working_path.

        Move slowly on slow tiles.
        """
        # Update self.x and self.y to be the centre positions of this enemy unit.
        self.x = self.rect.left + 16
        self.y = self.rect.top + 32

        # Get current grid location, based on pixel position.
        loc = convert_pos_to_loc((self.x, self.y))

        # Determine movement speed. This is pixels per frame.
        speed = 2  # Default movement speed for non-slow traversable tiles.
        if self.grid[loc] == 'slow':
            speed *= 0.5

        # If there are remaining locations/waypoints left in self.working_path, follow them.
        if len(self.working_path) > 0:
            target = convert_loc_to_pos(self.working_path[0], 'centre')

            # x and y distances to target
            dx = target[0] - self.x
            dy = target[1] - self.y

            # When the distance to the target waypoint is 1 pixel, force-set movement speed to be 1.
            # This is necessary for preventing 'overshooting' - moving over the centre point of a
            # location/tile and becoming 'stuck' by oscillating around the centre point.
            if abs(dx) == 1 or abs(dy) == 1:
                speed = 1

            # Observation: At most, only one of dx and dy will be non-zero.
            if dx != 0:  # If this unit must move horizontally
                # Move by 1 or 2 pixels to the target's direction
                self.rect.move_ip(dx // abs(dx) * speed, 0)

            elif dy != 0:  # If this unit must move vertically
                # Move by 1 or 2 pixels to the target's direction
                self.rect.move_ip(0, dy // abs(dy) * speed)

            elif (self.x, self.y) == target:  # If the target location/waypoint has been reached
                self.working_path = self.working_path[1:]  # Remove this location/waypoint

    def draw_pathline(self, screen: pygame.Surface, colour: Tuple[int, int, int]) -> None:
        """Method to draw self.working_path onto the screen.
        The process is twofold:
            - draw a line from this enemy unit's current pixel position to the next
              location/waypoint in self.working_path
            - draw lines connecting each location/waypoint in self.working path.
        """
        if len(self.working_path) > 0:
            pygame.draw.line(screen, colour,
                             (self.x, self.y),
                             convert_loc_to_pos(self.working_path[0], 'centre'), 2)

        for i in range(len(self.working_path) - 1):
            pygame.draw.line(screen, colour,
                             convert_loc_to_pos(self.working_path[i], 'centre'),
                             convert_loc_to_pos(self.working_path[i + 1], 'centre'), 2)

    def set_loc(self, loc: Tuple[int, int]) -> None:
        """Set this enemy unit's position on-screen to the desired grid location.
        """
        self.rect.left = convert_loc_to_pos(loc, 'topleft')[0] + 16
        self.rect.top = convert_loc_to_pos(loc, 'topleft')[1]

    def get_loc(self) -> Tuple[int, int]:
        """Get this enemy unit's grid location.
        """
        return convert_pos_to_loc((self.x, self.y))

    def set_working_path(self, _path: List[Tuple[int, int]]) -> None:
        """Update this enemy unit's working_path with a new path.

        This method is always called in conjunction with set_loc,
        where the designated location is the first element in _path.

        Preconditions:
            - convert_pos_to_loc((self.x, self.y)) == _path[0]
        """
        self.working_path = _path[1:]  # As in __init__, remove the first element


class Tile(pygame.sprite.Sprite):
    """A tile (traversable, slow, goal, obstacle) which is to be drawn in batch on the screen.

    Tile dimensions are 64x64.

    Instance Attributes:
        - type: A string representing the type of this specific tile.
        - image: The pygame.image (surface) object of this tile.
        - rect: The pygame.rect object tied to self.image.
    """
    type: str
    image: pygame.image
    rect: pygame.rect

    def __init__(self, _type: str) -> None:
        """Initialise all instance attributes.
        Load appropriate sprite image according to self.type.

        Preconditions:
            - _type in {'traversable', 'slow', 'goal', 'obstacle'}
        """
        self.type = _type
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprite_' + self.type + '.png').convert()
        self.rect = self.image.get_rect()


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 100,
        'disable': ['E1136'],
        'extra-imports': ['pygame', 'tools'],
        'allowed-io': [],
        'max-nested-blocks': 4
    })
