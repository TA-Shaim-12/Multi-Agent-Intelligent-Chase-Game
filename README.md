# Multi-Agent-Intelligent-Chase-Game
Smart police vs thief chase game showcasing real-time AI decision-making using classic search algorithms and performance analytics.

# Dijkstra's Algorithm
By considering cost of each tile dijkstra finds the lowest costing path.
It explores more nodes than greedy and takes longer time but still guarantees optimal path based on terrain costs

# Greedy Best-First Search
By using heuristic function greedy determines node distance to each other. It explores the closest node to goal. Hence it is faster . But is ignores terrain costs and cant guarantee optimal path always. 

# Environment Drawing
The game environment is drawn using Pygame graphics instead of loading game graphics from outside files. Shapes, colors and animations are used to create different terrain types such as : tree, bushes, stones, mud, walls, collectibles, exits and characters. Slight differences are added to make the environment look more natural 

# Character Drawing
Characters (Police and Theif) are drawn using geometrical shapes.The cops and theives are drawn dynamically using geometric shapes. Movement of arms and legs are achieved by making them move with time and elements like badges, hats, hair and capture effects are added to define character types.
