def dijkstra_path(grid,start,goal): 

    dist={start:0}; #store cheapest path cost
    prev={start:None}; #store prev node
    pq=[(0,start)]; #priority queue (cost(cheapest),node)
    expanded=0 #counting visited nodes

    while pq: #iterate till no nodes are left to visit
        d,cur=heapq.heappop(pq);  #explores the current cheapest path and removes the lowest costing node. cur= current node, d= cur total path cost
        expanded+=1 #increase count