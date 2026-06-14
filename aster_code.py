def astar_path(grid,start,goal):
    open_set=[(_h(start,goal),0,start)]; came={start:None}; g={start:0}; expanded=0
    while open_set:
        _,gv,cur=heapq.heappop(open_set); expanded+=1
        if cur==goal:
            path=[]
            while cur and cur!=start: path.append(cur); cur=came[cur]
            return path[::-1],expanded
        for nb in _nb(grid,cur):
            ng=gv+_cost(grid,nb)
            if ng<g.get(nb,1e18): g[nb]=ng; came[nb]=cur; heapq.heappush(open_set,(ng+_h(nb,goal),ng,nb))
    return [],expanded

def hill_path(grid,start,goal):
    path=[start]; vis={start}; cur=start; expanded=0
    for _ in range(500):
        if cur==goal: return path[1:],expanded
        nbs=[nb for nb in _nb(grid,cur) if nb not in vis]
        if not nbs: break
        expanded+=1; best=min(nbs,key=lambda n:_h(n,goal))
        if _h(best,goal)>=_h(cur,goal): best=random.choice(nbs)
        vis.add(best); path.append(best); cur=best
    return path[1:],expanded