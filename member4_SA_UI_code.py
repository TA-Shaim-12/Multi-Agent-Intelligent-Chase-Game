import math
import random

# Algorithm: Simulated Annealing

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