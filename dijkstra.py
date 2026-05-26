def dijkstra_path(grid,start,goal): 

    dist={start:0}; #store cheapest path cost
    prev={start:None}; #store prev node
    pq=[(0,start)]; #priority queue (cost(cheapest),node)
    expanded=0 #counting visited nodes

    while pq: #iterate till no nodes are left to visit
        d,cur=heapq.heappop(pq);  #explores the current cheapest path and removes the lowest costing node. cur= current node, d= cur total path cost
        expanded+=1 #increase count

        if cur==goal: #stop if goal is reached
            path=[] #storing path in this list
            while cur and cur!=start: #backtracking from goal using 'prev' dictionary
                path.append(cur); #adding current node to path
                cur=prev[cur] #then moving backward to previous node
            return path[::-1],expanded #since the path was found by backtracking so the path is in reverse. Reversing it to get the accurate path before returning
        for nb in _nb(grid,cur): #_nb() checks and returns all valid neighbours near current node
            nd=d+_cost(grid,nb) #calculating new total cost required to move into this neighbor.
            #d= total cost till now, _cost(grid,nb)= cost needed for new node, nd= total new cost
            #for example, assuming,[TILES type] Empty = 1, STONE = 2, MUD   = 3
            # Now, current cost = 5 and if next tile is MUD, New total cost = 8 [prev cost = 5 + cost of MUD =3]

            if nd<dist.get(nb,1e18):  #if new path costs less then a better path is found
                #if a node isn't visited yet,assume old cost of neighbour is very large(infinity)
                dist[nb]=nd;
 #storing the new cost which is less
                prev[nb]=cur; #store prev node
                heapq.heappush(pq,(nd,nb)) #pushing updated path in the priority (min heap) queue. Here, min heap makes Dijkstra efficient as cheapest paths are explored first
                #nd = total new cost, nb = neighbour node

    return [],expanded #if no path exists then return empty path.