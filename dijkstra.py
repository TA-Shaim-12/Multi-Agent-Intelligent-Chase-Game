def dijkstra_path(grid,start,goal): 

    dist={start:0}; #store cheapest path cost
    prev={start:None}; #store prev node
    pq=[(0,start)]; #priority queue (cost(cheapest),node)
    expanded=0 #counting visited nodes