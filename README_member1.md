# Lab Assignment Report — Member 1
**ID:** 0112320064  
**Assigned Algorithm:** BFS (Breadth-First Search)

---

## Task Analytics: BFS vs Dijkstra's Algorithm

Our project simulates a Multi-Agent Chase Game where police officers use search algorithms to find and catch a thief. As Member 1, my task was to implement the BFS pathfinding algorithm. Below is my analysis based on the performance of my BFS code compared to Dijkstra's algorithm on different map conditions.

### 1. Which algorithm is faster in terms of execution time?
* **Dijkstra's Algorithm is faster** when we run the game on terrain maps. This happens because Dijkstra uses a priority queue and always checks the paths with lower movement weights first, so it quickly reaches the thief.
* **BFS is slower** in complex layouts. BFS does not look at tile weights, so it expands like a big circle in every direction. If the thief is far away on the map, BFS takes more time to process because it calculates too many positions level by level before deciding the actual path.

### 2. Which algorithm explores more nodes?
* **BFS explores a lot more nodes** on the grid. Because it searches layer by layer (flood-fill method), it must check every single walkable neighbor at distance 1, then distance 2, and so on. It basically searches almost the whole map until it finds the thief's coordinate.
* **Dijkstra explores fewer nodes** because it targets specific directions based on the lowest cost. It automatically avoids exploring heavy penalty areas like mud or stone if a cheaper route is available, keeping the total searched nodes low.

### 3. Which finds a better path on terrain maps like mud or stone?
* **Dijkstra finds a much better and optimal path** on terrain maps. In our code, tiles like `MUD` or `STONE` have higher movement costs. Dijkstra adds up these costs and intelligently guides the police agent *around* the mud or stone to find the fastest path.
* **BFS cannot find the best path** here. It only looks for the minimum number of blocks (hops), completely ignoring the terrain cost. So, it often makes the police walk straight through deep mud, which slows down the capture.

### 4. Does BFS care about terrain cost or not?
* **No, BFS does not care about terrain cost at all.** In theory and in our implementation, BFS treats the grid as an unweighted graph where every step has a default cost of 1.
* In my `bfs_path` code, the neighbor function (`_nb`) only checks if a tile is a solid obstacle (like a wall or tree) or a walkable space. If it is walkable, BFS treats it with the exact same priority, whether it is a normal road, mud, or stone.



