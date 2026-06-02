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
