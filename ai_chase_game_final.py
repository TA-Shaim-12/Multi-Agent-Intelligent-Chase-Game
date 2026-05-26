def adv_astar_path(grid,start,goal):
    RADIUS=18  # Defines the local search radius around the goal node.Inside this radius, Dijkstra is used to generate exact heuristic values.
    dist_map={goal:0}; pq=[(0,goal)]  # dist_map stores the shortest distance from each node to the goal. Do backward traversal.
    while pq:
        cost,node=heapq.heappop(pq)
        if cost>dist_map.get(node,1e18): continue   # Skip processing if a better path to this node already exists.
        if _h(node,goal)>RADIUS: continue           # Ignore nodes outside the predefined local radius.
        for nb in _nb(grid,node):
            new_cost=cost+_cost(grid,nb)            
            if new_cost<dist_map.get(nb,1e18):      # Update only if a shorter path is found.
                dist_map[nb]=new_cost
                heapq.heappush(pq,(new_cost,nb))
    def h_adv(pos):          # advanced heuristic function.
        return dist_map.get(pos,_h(pos,goal))   # exact if cached else Manhattan  # ── forward A* using enriched heuristic ──
    open_set=[(h_adv(start),0,start)]
    came={start:None}       # Store parent nodes for path reconstruction.
    g_cost={start:0}
    expanded=0
    while open_set:
        _,g,node=heapq.heappop(open_set)
        expanded+=1
        if node==goal:
            path=[]
            while node and node!=start:    # Backtrack from goal to start to reconstruct the path.
                path.append(node)
                node=came[node]
            return path[::-1],expanded     # reverse path to get correct order from start to goal.
        for nb in _nb(grid,node):          # Explore neighbors of the current node.
            new_g=g+_cost(grid,nb)
            if new_g<g_cost.get(nb,1e18):  # Update if a shorter route is discovered.
                g_cost[nb]=new_g
                came[nb]=node
                heapq.heappush(
                    open_set,
                    (new_g+h_adv(nb),new_g,nb)
                )
    return [],expanded