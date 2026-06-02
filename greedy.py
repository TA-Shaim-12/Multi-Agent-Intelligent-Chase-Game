def greedy_path(grid,start,goal):

    open_set=[(_h(start,goal),start)] #storing priority queue where node with smallest estimated distance will always be explored first.

    came={start:None}  #keeps track of prev node of visited nodes. start node has no parent, so it's set to None.
    #it's important as after reaching the goal, we can trace backwards 

    vis={start} #set of visited nodes. Prevents algo from visiting same cell repeatedly

    expanded=0 #counting visited nodes
