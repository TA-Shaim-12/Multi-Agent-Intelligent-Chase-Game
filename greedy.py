def greedy_path(grid,start,goal):

    open_set=[(_h(start,goal),start)] #storing priority queue where node with smallest estimated distance will always be explored first.

    came={start:None}  #keeps track of prev node of visited nodes. start node has no parent, so it's set to None.
    #it's important as after reaching the goal, we can trace backwards 

    vis={start} #set of visited nodes. Prevents algo from visiting same cell repeatedly

    expanded=0 #counting visited nodes
 while open_set: #iterates as long as there are nodes left to visit

        _,cur=heapq.heappop(open_set) #removes node with smallest estimated distance
        #greedy only looks at heuristic distance instead of actual cost

        expanded+=1 #increase count

        if cur==goal: #stop if goal is reached
            path=[] #storing path in this list

            while cur and cur!=start: #backtracking from goal using 'parent' dictionary
                path.append(cur) #adding current node into the path.
                cur=came[cur] #then moving backward to previous node

            return path[::-1],expanded #since the path was found by backtracking so the path is in reverse. Reversing it to get the accurate path before returning
        for nb in _nb(grid,cur): #explores neighbour cells

            if nb not in vis: #processes unvisited nodes only

                vis.add(nb) #marks as visited
                came[nb]=cur #stores current node as neighbour nodes parent
                heapq.heappush(open_set,(_h(nb,goal),nb)) #(_h(nb,goal))means heuristic distance from the neighbor node to the goal
                #adds neighbour into prio queue
                #abs(row diff)+abs(col diff)
                #it is the reason greedy is fast but may result poorly(since it uses heuristic cost, ignoring actual cost)

    return [],expanded #if no path exists then return empty path and explored .