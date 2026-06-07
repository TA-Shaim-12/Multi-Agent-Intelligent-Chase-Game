# =============================================================
# AI CHASE GAME  -  MEMBER 2  CODE FILE
# Algorithms: Dijkstra + A* + Greedy + Hill Climbing
#             + All Drawing Helper Functions
# Branch    : dijkstra_[your_student_ID]
# File name : member2_Dijkstra_Greedy_code.py
#
# WHAT YOU DO IN THIS FILE:
#   1. Add comments to every line of dijkstra_path()
#   2. Add comments to every line of astar_path()
#   3. Add comments to every line of greedy_path()
#   4. Add comments to every line of hill_path()
#   5. Add tree shadow to draw_tile() - TREE section
#   6. Add stone crack to draw_tile() - STONE section
#   7. Create README_member2.md (200-word analysis)
#
# NOTE: Lines 260-315 (SA and Adv A*) are Member 5's algorithms.
#       Do NOT modify those functions. Only add comments to your 4.
#
# DO NOT edit anything outside this file.
# When done: git add, git commit, git push, open Pull Request.
# =============================================================

def dijkstra_path(grid,start,goal):
    dist={start:0}; prev={start:None}; pq=[(0,start)]; expanded=0
    while pq:
        d,cur=heapq.heappop(pq); expanded+=1
        if cur==goal:
            path=[]
            while cur and cur!=start: path.append(cur); cur=prev[cur]
            return path[::-1],expanded
        for nb in _nb(grid,cur):
            nd=d+_cost(grid,nb)
            if nd<dist.get(nb,1e18): dist[nb]=nd; prev[nb]=cur; heapq.heappush(pq,(nd,nb))
    return [],expanded

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

def greedy_path(grid,start,goal):
    open_set=[(_h(start,goal),start)]; came={start:None}; vis={start}; expanded=0
    while open_set:
        _,cur=heapq.heappop(open_set); expanded+=1
        if cur==goal:
            path=[]
            while cur and cur!=start: path.append(cur); cur=came[cur]
            return path[::-1],expanded
        for nb in _nb(grid,cur):
            if nb not in vis: vis.add(nb); came[nb]=cur; heapq.heappush(open_set,(_h(nb,goal),nb))
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

def sa_path(grid,start,goal):
    cur=start; path=[start]; vis={start}; T=5.0; expanded=0
    for _ in range(600):
        if cur==goal: return path[1:],expanded
        nbs=_nb(grid,cur)
        if not nbs: break
        expanded+=1; cand=random.choice(nbs)
        delta=_h(cur,goal)-_h(cand,goal)
        if delta>0 or (T>0.01 and random.random()<math.exp(delta/T)):
            cur=cand; path.append(cur); vis.add(cur)
        T*=0.98
    fallback,fe=astar_path(grid,start,goal); return fallback,expanded+fe

def adv_astar_path(grid,start,goal):
    """Advanced A* — heuristic enriched with a local Dijkstra pre-computation.
    We run Dijkstra from 'goal' backwards over a small neighbourhood radius
    to get exact backward-costs, which are used as an admissible heuristic
    instead of the plain Manhattan distance.  Outside the radius we fall back
    to Manhattan.  This gives better path quality on cost-varied terrain."""
    RADIUS=18   # cells around goal to pre-compute exact costs
    # ── backward Dijkstra from goal (reversed edges, same cost) ──
    bdist={goal:0}; bpq=[(0,goal)]
    while bpq:
        d,cur=heapq.heappop(bpq)
        if d>bdist.get(cur,1e18): continue
        if _h(cur,goal)>RADIUS: continue
        for nb in _nb(grid,cur):
            nd=d+_cost(grid,nb)
            if nd<bdist.get(nb,1e18):
                bdist[nb]=nd; heapq.heappush(bpq,(nd,nb))
    def h_adv(pos):
        return bdist.get(pos, _h(pos,goal))   # exact if known, else Manhattan
    # ── forward A* with enriched heuristic ──────────────────────
    open_set=[(h_adv(start),0,start)]; came={start:None}; g={start:0}; expanded=0
    while open_set:
        _,gv,cur=heapq.heappop(open_set); expanded+=1
        if cur==goal:
            path=[]
            while cur and cur!=start: path.append(cur); cur=came[cur]
            return path[::-1],expanded
        for nb in _nb(grid,cur):
            ng=gv+_cost(grid,nb)
            if ng<g.get(nb,1e18):
                g[nb]=ng; came[nb]=cur
                heapq.heappush(open_set,(ng+h_adv(nb),ng,nb))
    return [],expanded


def compute_path(algo,grid,start,goal):
    t0=time.perf_counter()
    fn={BFS:bfs_path,DIJKSTRA:dijkstra_path,ASTAR:astar_path,GREEDY:greedy_path,HILL:hill_path,SA:sa_path,ADV_ASTAR:adv_astar_path}.get(algo,astar_path)
    path,nodes=fn(grid,start,goal)
    ANALYZER.record(algo,(time.perf_counter()-t0)*1000,len(path),nodes)
    return path

# ══════════════════════════════════════════════
#  DRAWING HELPERS
# ══════════════════════════════════════════════
def draw_sky(surf,weather,night=False):
    if night: top,bot=(5,5,20),(15,15,55)
    elif weather==STORMY: top,bot=(50,50,80),(80,80,110)
    elif weather==FOGGY: top,bot=(180,195,210),(210,220,230)
    elif weather==SNOWY: top,bot=(160,190,220),(200,215,235)
    else: top,bot=SKY_TOP,SKY_BOT
    sky_h=SCREEN_H//3
    for y in range(sky_h):
        t=y/sky_h; pygame.draw.line(surf,tuple(int(top[i]*(1-t)+bot[i]*t) for i in range(3)),(0,y),(SCREEN_W,y))
    if night:
        pygame.draw.circle(surf,(230,230,200),(SCREEN_W-80,55),22)
        pygame.draw.circle(surf,(15,15,45),(SCREEN_W-68,48),18)
        rng=random.Random(42)
        for _ in range(60): pygame.draw.circle(surf,(240,240,255),(rng.randint(0,SCREEN_W),rng.randint(0,sky_h-10)),rng.randint(1,2))
    elif weather==SUNNY:
        pygame.draw.circle(surf,SUN_COL,(SCREEN_W-80,60),30)
        for a in range(0,360,30):
            rx=int((SCREEN_W-80)+44*math.cos(math.radians(a))); ry=int(60+44*math.sin(math.radians(a)))
            pygame.draw.line(surf,SUN_COL,(SCREEN_W-80,60),(rx,ry),2)

def _soil(v,r,c): return [SOIL_DARK,SOIL_MID,SOIL_LIGHT,SOIL_MID][((r*7+c*13+v)%4)]

def draw_tile(surf,grid,variants,r,c,ox,oy):
    x=ox+c*TILE; y=oy+r*TILE; t=grid[r][c]; v=variants[r][c]
    base=_soil(v,r,c); pygame.draw.rect(surf,base,(x,y,TILE,TILE))
    for i in range(3):
        dark=tuple(max(0,base[j]-20) for j in range(3))
        pygame.draw.circle(surf,dark,(x+(c*17+i*11+v*5)%TILE,y+(r*13+i*7+v*3)%TILE),2)
    if t==EMPTY: return
    cx2,cy2=x+TILE//2,y+TILE//2
    if t==BUSH:
        for dx2,dy2,r2,col in[(-6,4,10,BUSH_DARK),(6,4,10,BUSH_DARK),(0,-2,12,BUSH_MID),(-8,0,9,BUSH_MID),(8,0,9,BUSH_MID),(0,-6,8,BUSH_LITE),(-4,-4,6,BUSH_LITE),(4,-4,6,BUSH_LITE)]:
            pygame.draw.circle(surf,col,(cx2+dx2,cy2+dy2),r2)
    elif t==STONE:
        c1=(100+v*8,100+v*5,95+v*6); c2=(140+v*6,138+v*5,130+v*4)
        pygame.draw.ellipse(surf,c1,(x+4,y+6,TILE-8,TILE-10)); pygame.draw.ellipse(surf,c2,(x+8,y+8,TILE-16,TILE-16))
        pygame.draw.line(surf,(80,80,75),(cx2-6,cy2-2),(cx2+4,cy2+4),2)
    elif t==MUD:
        pygame.draw.rect(surf,MUD_COL,(x+2,y+2,TILE-4,TILE-4))
        for i in range(4): pygame.draw.ellipse(surf,(60,40,20),(x+5+(c*11+i*9)%(TILE-10),y+5+(r*7+i*11)%(TILE-10),6,4))
    elif t==TREE:
        pygame.draw.rect(surf,(80,50,20),(cx2-3,cy2,6,14))
        for dx2,dy2,r2,col in[(0,-4,14,(20,90,15)),(-5,-2,10,(30,110,20)),(4,-6,9,(50,140,35)),(0,-10,7,(70,160,55))]:
            pygame.draw.circle(surf,col,(cx2+dx2,cy2+dy2),r2)
    elif t==WALL:
        pygame.draw.rect(surf,(80,75,70),(x+1,y+1,TILE-2,TILE-2))
        for brow in range(2):
            for bcol in range(2+brow%2):
                bx2=x+1+bcol*((TILE-2)//(2+brow%2)); by2=y+1+brow*((TILE-2)//2)
                bw2=(TILE-2)//(2+brow%2)-2; bh2=(TILE-2)//2-2
                pygame.draw.rect(surf,(100,95,90),(bx2,by2,bw2,bh2)); pygame.draw.rect(surf,(65,60,55),(bx2,by2,bw2,bh2),1)

def draw_collectible(surf,ctype,x,y,t):
    cx2,cy2=x+TILE//2,y+TILE//2; bob=int(4*math.sin(t*3)); col=COLLECTIBLE_COLS[ctype]
    if ctype==COIN:
        pygame.draw.circle(surf,col,(cx2,cy2+bob),9); pygame.draw.circle(surf,WHITE,(cx2-3,cy2-3+bob),3)
        pygame.draw.circle(surf,(180,140,0),(cx2,cy2+bob),9,2)
    elif ctype==NECKLACE:
        for i in range(8):
            a=i*math.pi/4; pygame.draw.circle(surf,col,(cx2+int(9*math.cos(a)),cy2+int(5*math.sin(a))+bob),3)
        pygame.draw.circle(surf,(200,180,250),(cx2,cy2+bob),4)
    elif ctype==MONEY:
        pygame.draw.rect(surf,col,(cx2-9,cy2-6+bob,18,13),border_radius=3)
        pygame.draw.rect(surf,(20,150,50),(cx2-9,cy2-6+bob,18,13),2,border_radius=3)
        fs=pygame.font.SysFont("Arial",9,bold=True); surf.blit(fs.render("$",True,(20,150,50)),(cx2-4,cy2-5+bob))
    elif ctype==GEM:
        pts=[(cx2,cy2-11+bob),(cx2+7,cy2-3+bob),(cx2+5,cy2+7+bob),(cx2-5,cy2+7+bob),(cx2-7,cy2-3+bob)]
        pygame.draw.polygon(surf,col,pts); pygame.draw.polygon(surf,WHITE,pts,1)
        pygame.draw.line(surf,WHITE,(cx2,cy2-11+bob),(cx2,cy2+7+bob),1)
    elif ctype==BOOST:
        glow=abs(math.sin(t*4))*0.5+0.5; c2=tuple(int(BOOST_COL[i]*glow) for i in range(3))
        pts=[(cx2,cy2-11+bob),(cx2+5,cy2-2+bob),(cx2+1,cy2-2+bob),(cx2+6,cy2+9+bob),(cx2-1,cy2+1+bob),(cx2+3,cy2+1+bob)]
        pygame.draw.polygon(surf,c2,pts); pygame.draw.polygon(surf,WHITE,pts,1)

def draw_exit(surf,x,y,t):
    glow=abs(math.sin(t*2))*80; col=(50,int(200+glow/2),int(100+glow/2))
    pygame.draw.rect(surf,col,(x+2,y+2,TILE-4,TILE-4),border_radius=6)
    pygame.draw.rect(surf,WHITE,(x+2,y+2,TILE-4,TILE-4),2,border_radius=6)
    fs=pygame.font.SysFont("Arial",11,bold=True); txt=fs.render("EXIT",True,WHITE)
    surf.blit(txt,(x+TILE//2-txt.get_width()//2,y+TILE//2-txt.get_height()//2))

def draw_character(surf,x,y,is_police,direction,anim_frame,captured=False,body_col=None,badge_col=None):
    if body_col is None: body_col=POLICE_BLUE if is_police else THIEF_ORA
    if badge_col is None: badge_col=GOLD if is_police else (180,30,30)
    skin=(220,175,130); cx2,cy2=x+TILE//2,y+TILE//2
    ls=int(7*math.sin(anim_frame*math.pi*2))
    pygame.draw.line(surf,(50,50,80),(cx2-5,cy2+8),(cx2-5+ls,cy2+20),4)
    pygame.draw.line(surf,(50,50,80),(cx2+5,cy2+8),(cx2+5-ls,cy2+20),4)
    pygame.draw.ellipse(surf,(30,25,20),(cx2-9+ls,cy2+17,8,5)); pygame.draw.ellipse(surf,(30,25,20),(cx2+1-ls,cy2+17,8,5))
    pygame.draw.rect(surf,body_col,(cx2-10,cy2-4,20,16),border_radius=4)
    pygame.draw.circle(surf,badge_col,(cx2,cy2+3),4)
    asw=int(5*math.sin(anim_frame*math.pi*2+math.pi))
    pygame.draw.line(surf,body_col,(cx2-10,cy2-2),(cx2-16,cy2+8+asw),4)
    pygame.draw.line(surf,body_col,(cx2+10,cy2-2),(cx2+16,cy2+8-asw),4)
    pygame.draw.circle(surf,skin,(cx2-16,cy2+8+asw),4); pygame.draw.circle(surf,skin,(cx2+16,cy2+8-asw),4)
    pygame.draw.rect(surf,skin,(cx2-4,cy2-8,8,8)); pygame.draw.circle(surf,skin,(cx2,cy2-14),12)
    if is_police:
        pygame.draw.rect(surf,POLICE_BLUE,(cx2-13,cy2-22,26,8),border_radius=3)
        pygame.draw.rect(surf,(20,40,140),(cx2-10,cy2-26,20,7),border_radius=3)
        pygame.draw.circle(surf,badge_col,(cx2,cy2-22),3)
    else:
        hair=(40,30,20) if body_col==THIEF_ORA else (80,10,120)
        pygame.draw.ellipse(surf,hair,(cx2-11,cy2-26,22,12))
        band=(180,30,30) if body_col==THIEF_ORA else (120,20,180)
        pygame.draw.rect(surf,band,(cx2-11,cy2-20,22,5),border_radius=2)
    ex=4 if direction==0 else(-4 if direction==1 else 0)
    pygame.draw.circle(surf,BLACK,(cx2+ex-3,cy2-16),2); pygame.draw.circle(surf,BLACK,(cx2+ex+3,cy2-16),2)
    pygame.draw.circle(surf,WHITE,(cx2+ex-3,cy2-16),1); pygame.draw.circle(surf,WHITE,(cx2+ex+3,cy2-16),1)
    if captured:
        pygame.draw.line(surf,RED,(cx2-14,cy2-28),(cx2+14,cy2+22),3)
        pygame.draw.line(surf,RED,(cx2+14,cy2-28),(cx2-14,cy2+22),3)
