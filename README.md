# Multi-Agent-Intelligent-Chase-Game
Smart police vs thief chase game showcasing real-time AI decision-making using classic search algorithms and performance analytics.


I am working on an Advanced A* implementation that uses Dijkstra’s algorithm for heuristic estimation.

# Advanced A* Algorithm + Game Engine

**Name:** Tanvir Ahmed Shaim
**Branch:** `advastar_0112430120`
**Role:** Developer + Integration Lead

---

## My Contribution

I was responsible for two parts of the project:

**1. Advanced A* Algorithm**
The most technically complex algorithm in the project. It runs in two phases:
- **Phase 1** — Backward Dijkstra from the goal, computing exact terrain costs within an 18-cell radius
- **Phase 2** — Forward A* using those exact costs as the heuristic instead of Manhattan distance

This produces fewer node expansions than regular A* on terrain-heavy maps while remaining admissible and optimal.

**2. Game Class — Full Engine**
The main controller that runs everything: initialization, game loop, event handling, update logic, rendering, and state management.

---

## Algorithm Analysis

| Metric | Advanced A* vs Regular A* |
|--------|--------------------------|
| Execution Time | Slightly slower (backward Dijkstra setup cost) |
| Nodes Expanded | Lower — tighter heuristic means less exploration |
| Path Quality | Better on mud/stone terrain maps |
| Optimality | Guaranteed — heuristic never overestimates |

**Why it beats A* on terrain maps:**
Regular A* uses Manhattan distance as h(n), which ignores terrain cost. Advanced A* replaces this with exact Dijkstra costs near the goal, so the algorithm knows which directions are actually cheaper. On open maps the difference is small. On Muddy Swamp or Rocky Desert the node count drops noticeably.

**Admissibility:** Inside the radius, h(n) = exact cost = never overestimates. Outside the radius, h(n) = Manhattan distance = also never overestimates. Therefore Advanced A* is both admissible and optimal.
 

---

## How to Run

```
pip install pygame
python ai_chase_game_final.py
```
