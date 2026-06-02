# Member 4 Contribution: Simulated Annealing and UI System

## Assigned Task
My assigned part of the project was Simulated Annealing pathfinding and UI improvement. I worked on the SA algorithm, menu tooltip system, HUD scoreboard, game over MVP officer display, and custom map save/load support.

## Simulated Annealing Explanation
Simulated Annealing is a probabilistic search algorithm. It uses a temperature value called T to control randomness. In this project, T starts from 5.0. When the temperature is high, the algorithm can sometimes accept bad moves. A bad move means moving farther from the goal. This helps the algorithm explore different routes and avoid getting stuck in local traps.

The temperature cools down using the formula T *= 0.98. As T becomes smaller, the algorithm becomes more focused on the goal. When T is near zero, bad moves are almost never accepted. Because SA uses random choices, it can produce different paths in different runs.

## A* Fallback
Simulated Annealing is not always guaranteed to find the goal. If it fails after 600 steps, the system uses A* as a fallback. A* is more reliable because it uses both actual cost and heuristic distance. This makes the final path more stable.

## Comparison with Hill Climbing
SA is better than Hill Climbing in maps with traps because it can accept worse moves sometimes. Hill Climbing only moves toward the closest neighbour, so it can get stuck easily near walls or dead ends. However, SA can also be unpredictable because of randomness. For reliable final pathfinding, A* is still better.

## UI Improvements
I added algorithm tooltips so users can understand each algorithm from the menu. I also added a mini-scoreboard in the HUD to show which player is leading. The game over screen now shows the MVP police officer based on captures. I also added save and load support for custom maps.

## Testing
I checked that all code was saved in my own branch and committed task by task. Each feature was separated into meaningful commits to clearly show my individual contribution.

## Member 4 Testing Checklist

- Checked Simulated Annealing pathfinding explanation.
- Checked detailed comments inside sa_path function.
- Checked algorithm tooltip descriptions.
- Checked mini scoreboard UI support.
- Checked MVP officer display logic.
- Checked save/load support for custom map editor.
- Confirmed Member 4 files are included in the pull request.
- Confirmed work is done from branch sa_0112320269.
