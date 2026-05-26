import math
import random
#-------------------------------------- PART_1: Algorithm: Simulated Annealing------------------------------------------

#Section: SA pathfinding with detailed explanation
def sa_path(grid, start, goal):
    # Current position initially starts from the starting cell
    cur = start

    # Path list stores the route taken by Simulated Annealing
    path = [start]

    # Visited set stores cells that SA has already visited
    vis = {start}

    # T is the starting temperature of Simulated Annealing
    # Higher temperature means the algorithm can explore more randomly
    T = 5.0

    # Expanded counts how many nodes/cells are checked by the algorithm
    expanded = 0

    # SA will try maximum 600 steps before using fallback
    for _ in range(600):

                # If current cell is the goal, return the path without the start cell
        if cur == goal:
            return path[1:], expanded

        # Get all valid neighbour cells from the current position
        nbs = _nb(grid, cur)

        # If no neighbour is available, the algorithm cannot move further
        if not nbs:
            break

        # Increase expanded count for performance analysis
        expanded += 1

        # Randomly select one neighbour as the candidate next move
        cand = random.choice(nbs)

        # Delta measures whether the candidate move is better or worse
        # If delta is positive, candidate is closer to the goal
        # If delta is negative, candidate is farther from the goal
        delta = _h(cur, goal) - _h(cand, goal)

        # If candidate is better, accept it directly
        # If candidate is worse, sometimes accept it using probability
        # math.exp(delta / T) controls the chance of accepting a bad move
        # At high T, bad moves are accepted more often for exploration
        # At low T, bad moves are almost rejected, so SA becomes focused
        if delta > 0 or (T > 0.01 and random.random() < math.exp(delta / T)):

            # Move current position to the selected candidate cell
            cur = cand

            # Add the accepted cell into the path
            path.append(cur)

            # Mark the accepted cell as visited
            vis.add(cur)

        # Cooling schedule of Simulated Annealing
        # Temperature decreases by multiplying with 0.98 every step
        T *= 0.98

    # If SA fails to reach the goal within 600 steps, A* fallback is used
    fallback, fe = astar_path(grid, start, goal)

    # Return the reliable A* fallback path and total expanded count
    return fallback, expanded + fe


# --------------------------------Task 2: Algorithm tooltips for draw_menu function--------------------------------------

# This dictionary explains each algorithm shortly for the menu tooltip.
# When the user hovers over an algorithm button, the matching text is shown.
ALGO_TIPS = {
    "BFS": "Shortest hops, ignores terrain cost",
    "Dijkstra": "Cheapest real cost, terrain-aware",
    "A*": "Cost plus heuristic, optimal and fast",
    "Greedy": "Beelines to goal, not optimal",
    "Hill Climbing": "Local search, can get stuck",
    "Sim. Annealing": "Probabilistic, explores diversely",
    "Adv A*": "Dijkstra-enriched heuristic, best paths",
}


def draw_algorithm_tooltip(surf, F, hovered, ALGORITHMS, CYAN, SCREEN_W, SCREEN_H):
    # Check whether the hovered item is an algorithm button
    if isinstance(hovered, tuple) and hovered[0] == "palgo":

        # Extract algorithm index from hovered value
        ai = hovered[1] % 10

        # Make sure the index is inside the algorithm list
        if ai < len(ALGORITHMS):

            # Get tooltip text for the selected algorithm
            tip = ALGO_TIPS.get(ALGORITHMS[ai], "")

            # Draw the tooltip text at the bottom center of the menu screen
            surf.blit(
                F["sml"].render(tip, True, CYAN),
                (SCREEN_W // 2 - 200, SCREEN_H - 36)
            )




#-----------------------------------Task 3: Mini scoreboard for HUD----------------------------------------

def draw_mini_scoreboard(surf, F, t1, t2, SCREEN_W, SCREEN_H,
                         THIEF_ORA, THIEF2_COL, GOLD):
    # Compare Player 1 and Player 2 scores
    # This section decides who is leading the match

    if t1.score > t2.score:
        # Player 1 is leading
        leader = f"P1 leads +{t1.score - t2.score}"

        # Use Player 1 thief color for the lead text
        lead_col = THIEF_ORA

    elif t2.score > t1.score:
        # Player 2 is leading
        leader = f"P2 leads +{t2.score - t1.score}"

        # Use Player 2 thief color for the lead text
        lead_col = THIEF2_COL

    else:
        # Both players have equal score
        leader = "Tied!"

        # Use gold color when the game is tied
        lead_col = GOLD

    # Draw the mini scoreboard at the bottom center of the screen
    surf.blit(
        F["sml"].render(leader, True, lead_col),
        (SCREEN_W // 2 - 60, SCREEN_H - 24)
    )