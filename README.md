# Multi-Agent-Intelligent-Chase-Game
Smart police vs thief chase game showcasing real-time AI decision-making using classic search algorithms and performance analytics.
Member 3 Contribution (A* Search + Hill Climbing)


1. A* Search Function Documentation

You must find the astar_path() function and add detailed comments explaining how it works.

What A* Does

A* is a pathfinding algorithm used by the police officers to chase the thief.

It uses:

f(n) = g(n) + h(n)

Where:

g(n) = actual cost from the starting position to the current position

h(n) = estimated cost from current position to the goal

f(n) = total priority score


Heuristic Used

The heuristic is Manhattan Distance:

h(n)=|row_1-row_2|+|col_1-col_2|


Why A* Is Good

Finds the shortest path

Avoids unnecessary exploration

Faster than many traditional search methods

Reliable in complex maps

2. Hill Climbing Function Documentation

You must find hill_path() and add comments.

What Hill Climbing Does

Hill Climbing always chooses the neighboring cell that appears closest to the target.

It does NOT explore the entire map.

Advantages

Very fast

Simple implementation

Low memory usage


Disadvantages

Can get stuck in dead ends

Can get trapped in local optimum

Doesn't guarantee a path exists


When stuck, the code randomly chooses another neighbor to escape.

3. Thief Mud Penalty System

You must modify the Thief class.

Add

self.stun_timer = 0.0

inside _init_.

Update Timer

At the top of handle_input():

self.stun_timer = max(0, self.stun_timer - dt)

This continuously reduces the stun duration.

Modify Speed

Replace speed code with:

if self.stun_timer > 0:
    spd_mult = 0.5
elif self.boost_timer > 0:
    spd_mult = 1.8
else:
    spd_mult = 1.0

self.speed = self.base_speed * spd_mult

What Happens

State	Speed

Normal	100%
Boost	180%
Mud	50%

Apply Mud Effect

After:

self.r, self.c, self.dir = nr2, nc2, d

add:

if grid[self.r][self.c] == MUD:
    self.stun_timer = 1.5

Result

Whenever the thief steps on mud:

Speed becomes half

Effect lasts 1.5 seconds


This makes escaping harder.

4. Police Stuck Detection System

You must improve the Police AI.

What Happens

Suppose police is blocked:

Police cannot move.

After 2 seconds:

Current path is deleted

AI recalculates a new path

Police becomes smarter


