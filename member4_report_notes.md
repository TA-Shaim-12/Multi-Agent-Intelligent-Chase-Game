# Member 4 Report Notes

## Project Name
Multi-Agent Intelligent Chase Game

## Member Role
Member 4 — Simulated Annealing + UI System

## Branch Name
sa_0112320269

## Contribution Summary
My responsibility was to work on the Simulated Annealing pathfinding explanation and UI system improvements. I completed my work in a separate branch named sa_0112320269 and opened a pull request for review.

## Algorithm Contribution
I worked on the Simulated Annealing pathfinding part of the project. I added detailed comments to the sa_path function so that the logic of the algorithm becomes easier to understand.

Simulated Annealing is a probabilistic search technique. It uses a temperature value to control randomness. At high temperature, the algorithm can sometimes accept worse moves. This helps the agent explore different paths and avoid local traps. As the temperature decreases, the algorithm becomes more focused on better moves.

## A* Fallback Explanation
Simulated Annealing may not always find the final goal because it has randomness. For this reason, A* fallback is useful. A* is more reliable because it uses actual cost and heuristic distance to find a stable path.

## UI Contribution
I added several UI-related improvements:
- Algorithm tooltip descriptions
- Mini scoreboard support
- MVP officer display
- Save/load support for custom map editor

## Importance of UI Features
The algorithm tooltip helps users understand which algorithm is being used. The mini scoreboard helps show performance during the game. The MVP officer display shows the best-performing officer. The save/load feature helps users reuse custom maps for testing and demonstration.

## GitHub Contribution
I made meaningful commits in my own branch and opened a pull request from sa_0112320269 for review. I avoided fake commits and kept my work separate from the main branch.

## Final Status
My Member 4 work is complete and waiting for review through the pull request.
