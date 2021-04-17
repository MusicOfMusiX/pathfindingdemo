"""CSC111 Winter 2021 Project - main.py

PLEASE REFER TO THE [COMPUTATIONAL OVERVIEW] SECTION IN THE REPORT BEFORE READING DOCSTRINGS!

OBJECTIVE: Run the main game loop, allowing for an interactive visualisation of Dijkstra's Algorithm
and A* pathfinding on a 16x9 grid map.

This file is Copyright (c) 2021 Hyun Jo (Joshua) Jang.
"""
import random
from typing import List, Tuple, Dict

import pygame

import vertex_graph
import gameobjects
from pathfinding import a_star_pathfinding
from tools import convert_pos_to_loc


def refresh_enemies(enemies: List[gameobjects.Enemy],
                    grid: Dict[Tuple[int, int], str],
                    graph: vertex_graph.WeightedGraph) -> None:
    """For all enemies deployed on-screen,
    snap their positions to the centre of their nearest/current grid,
    and update their grid and path information.

    Called when there is a change in map state:
        - pathfinding algorithm change
        - change in tile type
    """

    for enemy in enemies:
        enemy.set_loc(enemy.get_loc())  # Snap to current tile centre
        enemy.grid = grid  # Update grid
        path = a_star_pathfinding(graph, enemy.get_loc(), is_dstra)  # Calculate new path
        enemy.set_working_path(path)  # Update path


if __name__ == '__main__':
    # Initialise pygame
    pygame.init()

    # Set up clock for manual framerate
    clock = pygame.time.Clock()

    # NOTE: ALL CONSTANTS DEFINED IN THIS PROJECT SHOULD NOT BE CHANGED.
    # UNFORTUNATELY, THESE VALUES ARE HARD-CODED AND MODIFYING THEM *WILL* BREAK THE PROGRAM.
    SCREEN_WIDTH = 1024  # 64 * 16
    SCREEN_HEIGHT = 704  # 64 * 11

    GRID_WIDTH = 16
    GRID_HEIGHT = 9

    GOAL_LOC = (15, 4)

    # Create screen.
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Create tiles for drawing later.
    tiles = {'normal': gameobjects.Tile('normal'),
             'goal': gameobjects.Tile('goal'),
             'obstacle': gameobjects.Tile('obstacle'),
             'slow': gameobjects.Tile('slow')}

    # Create UI images for frawing later.
    ui_top_1 = pygame.image.load('assets/sprite_ui_top_1.png').convert()
    ui_top_2 = pygame.image.load('assets/sprite_ui_top_2.png').convert()
    ui_bottom_1 = pygame.image.load('assets/sprite_ui_bottom_1.png').convert()
    warning_nodeploy = pygame.image.load('assets/sprite_warning_nodeploy.png').convert()
    warning_nochange = pygame.image.load('assets/sprite_warning_nochange.png').convert()

    # Create a dict-based grid representation of the game map to be used throughout the program.
    # Randomly distribute tile types.
    meta_grid = {}
    for i in range(GRID_WIDTH):
        for j in range(GRID_HEIGHT):
            meta_grid[(i, j)] = random.choice(['normal', 'normal', 'slow', 'slow', 'obstacle'])
    meta_grid[GOAL_LOC] = 'goal'

    # Create graph-based representation of the game map to be used throughout the program.
    meta_graph = vertex_graph.dict_to_graph(meta_grid)

    # Create list for storing enemy instances.
    meta_enemies = []

    # Define runtime-critical variables which tells the game loop what to do in every frame.
    running = True  # The main loop is broken when this is False.
    is_dstra = True  # Current pathfinding mode. True for Dijkstra, False for A*.
    drawcolour = (0, 0, 255)  # Current path-line draw colour. Blue for Dijkstra, Red for A*.

    # Define timers for use in 2-second warning pop-ups.
    warning_nodeploy_timer = 0
    warning_nochange_timer = 0

    # Main loop starts here
    while running:
        """
        The Event Handling section below is rather long and has multiple nested statements.
        However, it did not warrant a dedicated helper function because:
        - the code block is only used once in the entire program
        - the code is reasonably readable through the help of comments
        - moving the code into a helper function would mean passing in 6 arguments (e.g. meta_grid),
          which can become messy
            - this problem can be avoided through global variables, but PythonTA doesn't like that.
        """
        # ------------Event Handling------------
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                # ------------Left Click (deploy new enemy unit)------------
                if event.button == 1:
                    x = event.pos[0]
                    y = event.pos[1]
                    loc = convert_pos_to_loc((x, y))

                    ingrid = loc in meta_grid
                    # When clicked on a deployable tile
                    if ingrid and (meta_grid[loc] == 'slow' or meta_grid[loc] == 'normal'):
                        # If there exists a path from this location to the goal, add new enemy.
                        if meta_graph.connected(loc, GOAL_LOC):
                            if len(meta_enemies) < 5:  # Only add under the 5-enemy limit
                                new_path = a_star_pathfinding(meta_graph, loc, is_dstra)
                                new_enemy = gameobjects.Enemy(new_path, loc, meta_grid)
                                meta_enemies.append(new_enemy)

                        else:  # Show the "cannot deploy" warning message
                            warning_nodeploy_timer = 120  # 2 seconds

                    # When the algorithm swap button is clicked
                    elif x >= 716 and y <= 64:
                        is_dstra = not is_dstra
                        refresh_enemies(meta_enemies, meta_grid, meta_graph)

                # ------------Right Click (cycle through tile types)------------
                elif event.button == 3:
                    x = event.pos[0]
                    y = event.pos[1]
                    loc = convert_pos_to_loc((x, y))

                    ingrid = loc in meta_grid
                    # When clicked on a slow traversable tile, want to change into an obstacle.
                    if ingrid and meta_grid[loc] == 'slow':
                        # Test if this new obstacle tile allows for
                        # deployed enemies to reach their goal.
                        temp_grid = meta_grid.copy()
                        temp_grid[loc] = 'obstacle'
                        temp_graph = vertex_graph.dict_to_graph(temp_grid)

                        # Get all current enemy locations
                        enemy_loc_list = [enemy.get_loc() for enemy in meta_enemies]

                        # Test if all enemies can reach their goal from their current location
                        if all([temp_graph.connected(tloc, GOAL_LOC) for tloc in enemy_loc_list]):
                            # If yes, apply the change in tile to the 'real' meta_grid.
                            meta_grid[loc] = 'obstacle'

                            # Update meta_graph with new meta_grid
                            meta_graph = vertex_graph.dict_to_graph(meta_grid)
                            refresh_enemies(meta_enemies, meta_grid, meta_graph)

                        else:  # Show the "cannot block completely" warning message
                            warning_nochange_timer = 120  # 2 seconds

                    # Unlike above, changing to a traversable/non-obstacle tile
                    # does not require checking.
                    elif ingrid and meta_grid[loc] == 'normal':
                        meta_grid[loc] = 'slow'

                        # Update meta_graph with new meta_grid
                        meta_graph = vertex_graph.dict_to_graph(meta_grid)
                        refresh_enemies(meta_enemies, meta_grid, meta_graph)

                    elif ingrid and meta_grid[loc] == 'obstacle':
                        meta_grid[loc] = 'normal'

                        # Update meta_graph with new meta_grid
                        meta_graph = vertex_graph.dict_to_graph(meta_grid)
                        refresh_enemies(meta_enemies, meta_grid, meta_graph)

            # When the player presses the quit window button.
            elif event.type == pygame.QUIT:
                running = False

        # ------------Drawing & Updates------------
        # Draw all tiles.
        for i in range(GRID_WIDTH):
            for j in range(GRID_HEIGHT):
                screen.blit(tiles[meta_grid[(i, j)]].image, (i * 64, 64 + j * 64))

        # Update and draw all enemies.
        for alive_enemy in meta_enemies:
            alive_enemy.update()
            alive_enemy.draw_pathline(screen, drawcolour)
            screen.blit(alive_enemy.image, alive_enemy.rect)

            # Remove enemy if reached goal tile.
            if alive_enemy.get_loc() == GOAL_LOC:
                meta_enemies.remove(alive_enemy)

        # Draw upper UI section (one with the algorithm swap button).
        if is_dstra:
            screen.blit(ui_top_1, (0, 0))
        else:
            screen.blit(ui_top_2, (0, 0))

        # Draw lower UI section (warnings)
        if warning_nochange_timer > warning_nodeploy_timer:  # Implies that at least one is nonzero
            screen.blit(warning_nochange, (0, 640))
        elif warning_nochange_timer < warning_nodeploy_timer:
            screen.blit(warning_nodeploy, (0, 640))
        else:
            screen.blit(ui_bottom_1, (0, 640))

        # Decrement warning timer per frame. This allows for timed pop-ups.
        if warning_nodeploy_timer > 0:
            warning_nodeploy_timer -= 1
        if warning_nochange_timer > 0:
            warning_nochange_timer -= 1

        # Update path-line draw colour.
        if is_dstra:
            drawcolour = (0, 0, 255)
        else:
            drawcolour = (255, 0, 0)

        # Update entire screen with the above changes.
        pygame.display.flip()

        # Let this frame run such that the framerate becomes 60FPS.
        clock.tick(60)

    # Checking
    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 100,
        'disable': ['E1136', 'W0105'],
        'extra-imports':
            ['random', 'pygame', 'vertex_graph', 'gameobjects', 'pathfinding', 'tools'],
        'allowed-io': [],
        'max-nested-blocks': 8,
        'generated-members': ['pygame.*']
    })
