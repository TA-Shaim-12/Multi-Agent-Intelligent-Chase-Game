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
        