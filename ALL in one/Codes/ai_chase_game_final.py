"""
AI Police vs Thief Chase Game
============================================================
AI Lab Project — Algorithm-Based Category
Requirements: Python 3.8+, pygame 2.x
Install:  pip install pygame
Run:      python ai_chase_game_final.py

Controls
  Player 1 : Arrow Keys or WASD
  Player 2 : I / J / K / L  or  Numpad 8/4/5/6
  P        : Pause          R : Restart
  ESC      : Back to menu   Tab: Show Algorithm Analysis
"""

import pygame, sys, math, random, heapq, array as _array, time
from collections import deque
from dataclasses  import dataclass, field
from typing       import List, Tuple, Optional, Dict

SCREEN_W, SCREEN_H = 1380, 820
TILE = 30; FPS = 60

SKY_TOP=(100,180,255); SKY_BOT=(180,220,255); SOIL_DARK=(92,64,36); SOIL_MID=(115,84,48)
SOIL_LIGHT=(140,105,62); MUD_COL=(80,55,30); BUSH_DARK=(30,100,20); BUSH_MID=(50,150,35)
BUSH_LITE=(80,180,60); POLICE_BLUE=(30,60,180); THIEF_ORA=(220,100,10); THIEF2_COL=(160,30,200)
GOLD=(255,200,30); SUN_COL=(255,240,100); WHITE=(255,255,255); BLACK=(0,0,0)
RED=(220,40,40); GREEN=(40,200,80); YELLOW=(255,220,0); CYAN=(60,220,220)
GRAY=(160,160,160); ORANGE=(255,140,0); RAIN_COL=(120,160,220,180); SNOW_COL=(240,245,255,200)
BOOST_COL=(255,80,200); DIAMOND=(100,220,255)

# Distinct badge colours per officer slot
POLICE_BADGE_COLS=[(255,200,30),(255,100,30),(30,220,180),(220,60,220),(100,255,80)]

EMPTY=0; BUSH=1; STONE=2; MUD=3; TREE=4; WALL=5
TILE_NAMES={EMPTY:"Empty",WALL:"Wall",BUSH:"Bush",STONE:"Stone",MUD:"Mud",TREE:"Tree"}
TILE_PALETTE=[EMPTY,WALL,BUSH,STONE,MUD,TREE]
TILE_COLORS={EMPTY:(60,50,40),WALL:(90,80,70),BUSH:(40,120,30),STONE:(110,110,100),MUD:(80,55,30),TREE:(30,90,20)}

COIN="coin"; NECKLACE="necklace"; MONEY="money"; BOOST="boost"; GEM="gem"
COLLECTIBLE_VALUES={COIN:10,NECKLACE:50,MONEY:25,BOOST:0,GEM:100}
COLLECTIBLE_COLS={COIN:GOLD,NECKLACE:CYAN,MONEY:GREEN,BOOST:BOOST_COL,GEM:DIAMOND}

SUNNY="sunny"; RAINY="rainy"; SNOWY="snowy"; FOGGY="foggy"; STORMY="stormy"
WEATHERS=[SUNNY,RAINY,SNOWY,FOGGY,STORMY]

BFS="BFS"; DIJKSTRA="Dijkstra"; ASTAR="A*"; GREEDY="Greedy"; HILL="Hill Climbing"; SA="Sim. Annealing"
ADV_ASTAR="Adv A*"   # Advanced A* — Dijkstra-weighted heuristic
ALGORITHMS=[BFS,DIJKSTRA,ASTAR,GREEDY,HILL,SA,ADV_ASTAR]

# NEW: police count options
POLICE_COUNT_OPTIONS=[1,2,3,5]

MAPS=["Forest Chase","Rocky Desert","Muddy Swamp","Urban Grid","Mountain Pass","Custom"]
M_DEFAULT="Default"; M_DAY="Day"; M_NIGHT="Night"
DAY_NIGHT_MODES=[M_DEFAULT,M_DAY,M_NIGHT]
EASY="Easy"; MEDIUM="Medium"; HARD="Hard"
DIFFICULTIES=[EASY,MEDIUM,HARD]
DIFF_POLICE_SPEED={EASY:1.0,MEDIUM:1.8,HARD:2.8}
DIFF_COLLECTIBLE_MULT={EASY:3,MEDIUM:2,HARD:2}

# ══════════════════════════════════════════════
#  ALGORITHM ANALYZER
# ══════════════════════════════════════════════
@dataclass
class AlgoStats:
    name:str; total_time_ms:float=0.0; calls:int=0; total_nodes:int=0
    captures:int=0; path_lengths:List[int]=field(default_factory=list)
    convergence_log:List[float]=field(default_factory=list)
    @property
    def avg_time_ms(self): return self.total_time_ms/self.calls if self.calls else 0
    @property
    def avg_nodes(self): return self.total_nodes/self.calls if self.calls else 0
    @property
    def avg_path_len(self): return sum(self.path_lengths)/len(self.path_lengths) if self.path_lengths else 0
    @property
    def efficiency(self): return round(self.avg_path_len/max(self.avg_nodes,1),4)
    @property
    def solution_quality(self): return round(min(100,self.efficiency*100),1)

class AlgorithmAnalyzer:
    def __init__(self):
        self.stats:Dict[str,AlgoStats]={a:AlgoStats(a) for a in ALGORITHMS}
        self.session_log:List[dict]=[]
    def record(self,algo,elapsed_ms,path_len,nodes):
        s=self.stats[algo]; s.total_time_ms+=elapsed_ms; s.calls+=1
        s.total_nodes+=nodes; s.path_lengths.append(path_len); s.convergence_log.append(elapsed_ms)
        self.session_log.append({"algo":algo,"ms":elapsed_ms,"path":path_len,"nodes":nodes})
    def record_capture(self,algo):
        if algo in self.stats: self.stats[algo].captures+=1
    def summary(self):
        rows=[]
        for a in ALGORITHMS:
            s=self.stats[a]
            conv=round(sum(s.convergence_log[-10:])/max(len(s.convergence_log[-10:]),1),4) if s.convergence_log else 0
            rows.append({"Algorithm":a,"Calls":s.calls,"Avg Time (ms)":round(s.avg_time_ms,4),
                         "Avg Path Len":round(s.avg_path_len,1),"Avg Nodes":round(s.avg_nodes,1),
                         "Captures":s.captures,"Efficiency":s.efficiency,
                         "Sol. Quality":s.solution_quality,"Convergence":f"{conv}ms"})
        return rows

ANALYZER=AlgorithmAnalyzer()

# ══════════════════════════════════════════════
#  PARTICLE SYSTEM
# ══════════════════════════════════════════════
@dataclass
class Particle:
    x:float; y:float; vx:float; vy:float; life:float; col:tuple; size:float

class ParticleSystem:
    def __init__(self): self.particles:List[Particle]=[]
    def emit(self,x,y,col,count=6,spread=2.5):
        for _ in range(count):
            self.particles.append(Particle(x+random.uniform(-4,4),y+random.uniform(-4,4),
                random.uniform(-spread,spread),random.uniform(-spread*1.5,0),1.0,col,random.uniform(2,5)))
    def update(self,dt):
        for p in self.particles: p.x+=p.vx; p.y+=p.vy; p.vy+=0.08; p.life-=dt*1.5
        self.particles=[p for p in self.particles if p.life>0]
    def draw(self,surf):
        for p in self.particles:
            s=max(1,int(p.size*p.life)); tmp=pygame.Surface((s*2,s*2),pygame.SRCALPHA)
            pygame.draw.circle(tmp,(*p.col[:3],int(p.life*255)),(s,s),s); surf.blit(tmp,(int(p.x)-s,int(p.y)-s))

# ══════════════════════════════════════════════
#  WEATHER SYSTEM
# ══════════════════════════════════════════════
class WeatherSystem:
    def __init__(self,wtype=SUNNY):
        self.weather=wtype; self.drops=[]; self.flakes=[]
        self.thunder_timer=0; self.thunder_flash=0; self.wind=random.uniform(-1,1); self._init()
    def _init(self):
        self.drops=[]; self.flakes=[]
        if self.weather in(RAINY,STORMY):
            self.drops=[[random.randint(0,SCREEN_W),random.randint(-SCREEN_H,0),random.uniform(8,15),random.randint(10,20)] for _ in range(350)]
        if self.weather==SNOWY:
            self.flakes=[[random.randint(0,SCREEN_W),random.randint(0,SCREEN_H),random.uniform(1,3),random.randint(2,5)] for _ in range(220)]
    def set(self,w): self.weather=w; self._init()
    def update(self,dt):
        if self.weather in(RAINY,STORMY):
            for d in self.drops:
                d[1]+=d[2]; d[0]+=self.wind
                if d[1]>SCREEN_H: d[1]=random.randint(-80,0); d[0]=random.randint(0,SCREEN_W)
            if self.weather==STORMY:
                self.thunder_timer-=dt
                if self.thunder_timer<=0: self.thunder_flash=random.uniform(0.05,0.15); self.thunder_timer=random.uniform(5,20)
                if self.thunder_flash>0: self.thunder_flash-=dt
        if self.weather==SNOWY:
            for f in self.flakes:
                f[1]+=f[2]; f[0]+=math.sin(f[1]*0.02)*0.6
                if f[1]>SCREEN_H: f[1]=0; f[0]=random.randint(0,SCREEN_W)
    def draw_overlay(self,surf,night=False):
        if night:
            ov=pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA); ov.fill((0,0,20,130)); surf.blit(ov,(0,0))
        if self.weather==FOGGY:
            fog=pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA); fog.fill((200,215,220,80)); surf.blit(fog,(0,0))
        if self.weather in(RAINY,STORMY):
            for d in self.drops: pygame.draw.line(surf,RAIN_COL,(int(d[0]),int(d[1])),(int(d[0])-int(self.wind*2),int(d[1])+d[3]),1)
        if self.weather==SNOWY:
            for f in self.flakes: pygame.draw.circle(surf,SNOW_COL,(int(f[0]),int(f[1])),f[3])
        if self.weather==STORMY and self.thunder_flash>0:
            fl=pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA); fl.fill((240,240,255,int(min(180,self.thunder_flash*1200)))); surf.blit(fl,(0,0))
    def visibility(self): return {SUNNY:1.0,RAINY:0.7,SNOWY:0.6,FOGGY:0.4,STORMY:0.5}.get(self.weather,1.0)

# ══════════════════════════════════════════════
#  MAP GENERATOR
# ══════════════════════════════════════════════
def generate_map(name,cols,rows):
    grid=[[EMPTY]*cols for _ in range(rows)]; variants=[[0]*cols for _ in range(rows)]
    random.seed(hash(name)+random.randint(0,9999))
    cfg={"Forest Chase":([BUSH,TREE,BUSH,BUSH],0.18),"Rocky Desert":([STONE,STONE,MUD],0.15),
         "Muddy Swamp":([MUD,BUSH,MUD],0.22),"Urban Grid":([WALL,STONE],0.20),"Mountain Pass":([STONE,WALL,BUSH],0.17)}
    obs,density=cfg.get(name,([BUSH,STONE],0.15))
    for r in range(rows):
        for c in range(cols):
            if random.random()<density: grid[r][c]=random.choice(obs); variants[r][c]=random.randint(0,3)
    for _ in range(4):
        if random.random()<0.5:
            r=random.randint(1,rows-2)
            for c in range(cols): grid[r][c]=EMPTY
        else:
            c=random.randint(1,cols-2)
            for r in range(rows): grid[r][c]=EMPTY
    for c in range(cols): grid[0][c]=WALL; grid[rows-1][c]=WALL
    for r in range(rows): grid[r][0]=WALL; grid[r][cols-1]=WALL
    return grid,variants

# ══════════════════════════════════════════════
#  PATHFINDING
# ══════════════════════════════════════════════
def _nb(grid,pos):
    r,c=pos; rows=len(grid); cols=len(grid[0]); res=[]
    for dr,dc in[(-1,0),(1,0),(0,-1),(0,1)]:
        nr,nc=r+dr,c+dc
        if 0<=nr<rows and 0<=nc<cols and grid[nr][nc] not in(WALL,BUSH,TREE,STONE): res.append((nr,nc))
    return res

def _cost(grid,pos): return {MUD:3,STONE:2}.get(grid[pos[0]][pos[1]],1)
def _h(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])

def bfs_path(grid,start,goal):
    if start==goal: return [],0
    q=deque([[start]]); vis={start}; expanded=0
    while q:
        path=q.popleft(); cur=path[-1]; expanded+=1
        for nb in _nb(grid,cur):
            if nb==goal: return path[1:]+[nb],expanded
            if nb not in vis: vis.add(nb); q.append(path+[nb])
    return [],expanded

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
    """Advanced A* — heuristic improved using a local Dijkstra pre-computation.
    Dijkstra runs backward from the goal within a limited search radius
    to generate exact nearby path costs. These values are then used as
    an informed heuristic instead of only Manhattan distance. Outside
    the radius, Manhattan distance is used as fallback estimation."""
    RADIUS=18   # local area around goal for exact heuristic generation
    dist_map={goal:0}; pq=[(0,goal)]  # ── backward Dijkstra from goal ──
    while pq:
        cost,node=heapq.heappop(pq)
        if cost>dist_map.get(node,1e18): continue
        if _h(node,goal)>RADIUS: continue
        for nb in _nb(grid,node):
            new_cost=cost+_cost(grid,nb)
            if new_cost<dist_map.get(nb,1e18):
                dist_map[nb]=new_cost
                heapq.heappush(pq,(new_cost,nb))
    def h_adv(pos):          # advanced heuristic
        return dist_map.get(pos,_h(pos,goal))   # exact if cached else Manhattan  # ── forward A* using enriched heuristic ──
    open_set=[(h_adv(start),0,start)]
    came={start:None}
    g_cost={start:0}
    expanded=0
    while open_set:
        _,g,node=heapq.heappop(open_set)
        expanded+=1
        if node==goal:
            path=[]
            while node and node!=start:
                path.append(node)
                node=came[node]
            return path[::-1],expanded
        for nb in _nb(grid,node):
            new_g=g+_cost(grid,nb)
            if new_g<g_cost.get(nb,1e18):
                g_cost[nb]=new_g
                came[nb]=node
                heapq.heappush(
                    open_set,
                    (new_g+h_adv(nb),new_g,nb)
                )
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

# ══════════════════════════════════════════════
#  ENTITIES
# ══════════════════════════════════════════════
class Thief:
    P1_KEYS=[(pygame.K_UP,pygame.K_w),(pygame.K_DOWN,pygame.K_s),(pygame.K_LEFT,pygame.K_a),(pygame.K_RIGHT,pygame.K_d)]
    P2_KEYS=[(pygame.K_i,pygame.K_KP8),(pygame.K_k,pygame.K_KP5),(pygame.K_j,pygame.K_KP4),(pygame.K_l,pygame.K_KP6)]

    def __init__(self,r,c,player_index=1):
        self.r=r; self.c=c; self.px=float(c*TILE); self.py=float(r*TILE)
        self.base_speed=3.2; self.speed=self.base_speed; self.boost_timer=0.0
        self.dir=3; self.anim=0.0; self.move_cd=0.0; self.score=0; self.alive=True; self.escaped=False
        self.player_index=player_index; self.body_col=THIEF_ORA if player_index==1 else THIEF2_COL
        self.keys=self.P1_KEYS if player_index==1 else self.P2_KEYS

    def apply_boost(self): self.boost_timer=5.0

    def handle_input(self,keys,grid,dt):
        if not self.alive or self.escaped: return
        self.move_cd-=dt; self.boost_timer-=dt
        self.speed=self.base_speed*(1.8 if self.boost_timer>0 else 1.0)
        if self.move_cd>0: return
        dirs=[(self.r-1,self.c,2),(self.r+1,self.c,3),(self.r,self.c-1,1),(self.r,self.c+1,0)]
        for idx,(kr,ks) in enumerate(self.keys):
            if keys[kr] or keys[ks]:
                nr2,nc2,d=dirs[idx]
                if 0<=nr2<len(grid) and 0<=nc2<len(grid[0]):
                    if grid[nr2][nc2] not in(WALL,BUSH,TREE,STONE):
                        self.r,self.c,self.dir=nr2,nc2,d; self.anim+=0.25; self.move_cd=1.0/(self.speed*1.5)
                break

    def update(self,dt,ox,oy):
        tx=float(self.c*TILE+ox); ty=float(self.r*TILE+oy)
        self.px+=(tx-self.px)*min(1,dt*12); self.py+=(ty-self.py)*min(1,dt*12)

    def draw(self,surf):
        if self.boost_timer>0:
            glow=pygame.Surface((TILE+16,TILE+16),pygame.SRCALPHA)
            pygame.draw.circle(glow,(255,80,200,80),(TILE//2+8,TILE//2+8),TILE//2+6); surf.blit(glow,(int(self.px)-8,int(self.py)-8))
        draw_character(surf,int(self.px),int(self.py),False,self.dir,self.anim,not self.alive,body_col=self.body_col)

class Police:
    def __init__(self,r,c,algorithm=ASTAR,index=0):
        self.r=r; self.c=c; self.px=float(c*TILE); self.py=float(r*TILE)
        self.algorithm=algorithm; self.index=index
        self.base_speed=1.8; self.speed=self.base_speed
        self.dir=3; self.anim=0.0; self.path:List[Tuple]=[]
        self.path_timer=0.0; self.move_cd=0.0; self.nodes_explored=0; self.captures=0
        self.is_buffed=False; self.buff_timer=0.0; self.buff_cd=12.0

    def replan(self,grid,tr,tc,vis):
        start=(self.r,self.c); goal=(tr,tc)
        if _h(start,goal)>30*vis:
            nbs=_nb(grid,start); self.path=[random.choice(nbs)] if nbs else []
        else: self.path=compute_path(self.algorithm,grid,start,goal)
        self.nodes_explored+=max(1,len(self.path)); self.path_timer=0.6

    def update(self,grid,thieves,dt,vis,dn_mode,difficulty):
        self.path_timer-=dt; self.move_cd-=dt
        if dn_mode==M_DAY:
            self.buff_cd-=dt; self.buff_timer-=dt
            if self.buff_timer>0: self.speed=3.2*(DIFF_POLICE_SPEED[difficulty]/1.8)*2.2; self.is_buffed=True
            else:
                self.speed=3.2*(DIFF_POLICE_SPEED[difficulty]/1.8); self.is_buffed=False
                if self.buff_cd<=0: self.buff_cd=random.uniform(8,14); self.buff_timer=random.uniform(2.5,4.5)
        elif dn_mode==M_NIGHT: self.speed=DIFF_POLICE_SPEED[difficulty]*0.65; self.is_buffed=False
        else: self.speed=DIFF_POLICE_SPEED[difficulty]; self.is_buffed=False
        active=[th for th in thieves if th.alive and not th.escaped]
        if not active: return
        target=min(active,key=lambda th:_h((self.r,self.c),(th.r,th.c)))
        if self.path_timer<=0: self.replan(grid,target.r,target.c,vis)
        if self.path and self.move_cd<=0:
            nr,nc=self.path[0]
            if grid[nr][nc] not in(WALL,BUSH,TREE,STONE):
                dr=nr-self.r; dc=nc-self.c
                self.dir={(0,1):0,(0,-1):1,(-1,0):2,(1,0):3}.get((dr,dc),self.dir)
                self.r,self.c=nr,nc; self.path.pop(0); self.anim+=0.25
            else: self.path.clear()
            self.move_cd=1.0/(self.speed*1.5)

    def update_pixel(self,ox,oy,dt):
        tx=float(self.c*TILE+ox); ty=float(self.r*TILE+oy)
        self.px+=(tx-self.px)*min(1,dt*10); self.py+=(ty-self.py)*min(1,dt*10)

    def draw(self,surf):
        badge=POLICE_BADGE_COLS[self.index%len(POLICE_BADGE_COLS)]
        if self.is_buffed:
            glow=pygame.Surface((TILE+20,TILE+20),pygame.SRCALPHA)
            pygame.draw.circle(glow,(255,220,50,100),(TILE//2+10,TILE//2+10),TILE//2+8); surf.blit(glow,(int(self.px)-10,int(self.py)-10))
        draw_character(surf,int(self.px),int(self.py),True,self.dir,self.anim,badge_col=badge)

# ══════════════════════════════════════════════
#  SESSION ANALYSIS SCREEN  (Tab key)
# ══════════════════════════════════════════════
def draw_analysis_screen(surf,fonts):
    surf.fill((10,12,28)); F=fonts
    surf.blit(F['title'].render("ALGORITHM COMPARATIVE ANALYSIS",True,GOLD),(40,20))
    surf.blit(F['sml'].render("Tab/ESC: close  |  Data collected live across all game sessions",True,GRAY),(40,80))
    summary=ANALYZER.summary()
    headers=["Algorithm","Calls","Avg Time(ms)","Avg Path","Avg Nodes","Captures","Efficiency","Sol.Quality","Convergence"]
    col_x=[30,155,255,375,475,585,680,775,880]
    for i,(h,cx) in enumerate(zip(headers,col_x)):
        pygame.draw.rect(surf,(30,50,90),(cx,108,col_x[min(i+1,len(col_x)-1)]-cx-2,28),border_radius=3)
        surf.blit(F['sml'].render(h,True,CYAN),(cx+3,114))
    algo_colors={BFS:(255,200,100),DIJKSTRA:(100,220,255),ASTAR:(100,255,150),GREEDY:(255,150,100),HILL:(200,100,255),SA:(255,100,150),ADV_ASTAR:(255,255,80)}
    for ri,row in enumerate(summary):
        ry=144+ri*34; pygame.draw.rect(surf,(25,28,45) if ri%2==0 else(20,22,38),(28,ry,SCREEN_W-56,30),border_radius=3)
        vals=[row["Algorithm"],str(row["Calls"]),str(row["Avg Time (ms)"]),str(row["Avg Path Len"]),
              str(row["Avg Nodes"]),str(row["Captures"]),str(row["Efficiency"]),str(row["Sol. Quality"]),str(row["Convergence"])]
        ac=algo_colors.get(row["Algorithm"],WHITE)
        for i,(v,cx) in enumerate(zip(vals,col_x)): surf.blit(F['sml'].render(v,True,ac if i==0 else WHITE),(cx+3,ry+7))
    chart_y=360; surf.blit(F['med'].render("Execution Time (ms) — lower is better",True,CYAN),(30,chart_y))
    max_t=max((s.avg_time_ms for s in ANALYZER.stats.values()),default=1) or 1
    for i,a in enumerate(ALGORITHMS):
        s=ANALYZER.stats[a]; bx=30+i*148; by=chart_y+28; col=algo_colors.get(a,WHITE)
        bh=int((s.avg_time_ms/max_t)*90) if max_t>0 else 0
        pygame.draw.rect(surf,(28,32,52),(bx,by,138,105),border_radius=4)
        if bh>0: pygame.draw.rect(surf,col,(bx+4,by+101-bh,130,bh),border_radius=3)
        surf.blit(F['sml'].render(a[:10],True,col),(bx+3,by+106)); surf.blit(F['sml'].render(f"{s.avg_time_ms:.4f}ms",True,GRAY),(bx+3,by+122))
    chart_y2=520; surf.blit(F['med'].render("Nodes Expanded — lower = more efficient",True,CYAN),(30,chart_y2))
    max_n=max((s.avg_nodes for s in ANALYZER.stats.values()),default=1) or 1
    for i,a in enumerate(ALGORITHMS):
        s=ANALYZER.stats[a]; bx=30+i*148; by=chart_y2+28; col=algo_colors.get(a,WHITE)
        bh=int((s.avg_nodes/max_n)*90) if max_n>0 else 0
        pygame.draw.rect(surf,(28,32,52),(bx,by,138,100),border_radius=4)
        if bh>0: pygame.draw.rect(surf,col,(bx+4,by+96-bh,130,bh),border_radius=3)
        surf.blit(F['sml'].render(a[:10],True,col),(bx+3,by+98)); surf.blit(F['sml'].render(f"{s.avg_nodes:.0f} nodes",True,GRAY),(bx+3,by+114))
    surf.blit(F['sml'].render("Efficiency=PathLen/Nodes  |  Sol.Quality=Efficiency×100  |  Convergence=avg ms of last 10 calls",True,GRAY),(30,SCREEN_H-24))

# ══════════════════════════════════════════════
#  POST-GAME ANALYSIS SCREEN
# ══════════════════════════════════════════════
def draw_postgame_analysis(surf, fonts, police_list, elapsed):
    surf.fill((8,10,24)); F=fonts
    surf.blit(F['title'].render("POST-GAME  ALGORITHM  ANALYSIS",True,GOLD),(40,18))
    surf.blit(F['sml'].render(
        f"Duration: {int(elapsed)//60:02d}:{int(elapsed)%60:02d}  |  Officers: {len(police_list)}  |  "
        "SPACE/Enter=Play Again   M=Menu   Tab=Session Stats", True,GRAY),(40,74))

    algo_colors={BFS:(255,200,100),DIJKSTRA:(100,220,255),ASTAR:(100,255,150),GREEDY:(255,150,100),HILL:(200,100,255),SA:(255,100,150),ADV_ASTAR:(255,255,80)}

    # ── Officer table ──
    headers=["Officer","Algorithm","Captures","Nodes Used","Avg Path Len","Efficiency"]
    col_x=[40,130,300,410,550,660]
    surf.blit(F['med'].render("Officer Performance This Game",True,CYAN),(40,108))
    for i,(h,cx) in enumerate(zip(headers,col_x)):
        nxt=col_x[min(i+1,len(col_x)-1)]
        pygame.draw.rect(surf,(30,50,90),(cx,130,nxt-cx-2,26),border_radius=3)
        surf.blit(F['sml'].render(h,True,WHITE),(cx+4,136))
    for ri,p in enumerate(police_list):
        ry=162+ri*30; bc=POLICE_BADGE_COLS[p.index%len(POLICE_BADGE_COLS)]
        pygame.draw.rect(surf,(22,26,42) if ri%2==0 else(18,21,36),(38,ry,690,26),border_radius=3)
        ac=algo_colors.get(p.algorithm,WHITE)
        avg_path=round(ANALYZER.stats[p.algorithm].avg_path_len,1)
        eff=ANALYZER.stats[p.algorithm].efficiency
        for val,cx in zip([f"Officer {ri+1}",p.algorithm,str(p.captures),str(p.nodes_explored),str(avg_path),str(eff)],col_x):
            surf.blit(F['sml'].render(val,True,bc if cx==40 else(ac if cx==130 else WHITE)),(cx+4,ry+6))

    # ── 4-metric bar charts ──
    panel_y=162+len(police_list)*30+24
    surf.blit(F['med'].render("Algorithm Comparative Metrics  (session totals)",True,CYAN),(40,panel_y))
    metrics=[
        ("Execution Time (ms)\nlower=faster",        lambda s:s.avg_time_ms,       True),
        ("Solution Quality\nhigher=better path",      lambda s:s.solution_quality,  False),
        ("Efficiency  path/nodes\nhigher=smarter",    lambda s:s.efficiency,        False),
        ("Convergence  last-10 avg ms\nlower=stable", lambda s:float(sum(s.convergence_log[-10:])/max(len(s.convergence_log[-10:]),1)) if s.convergence_log else 0, True),
    ]
    panel_y+=28; CHART_W=310; CHART_H=110; GAP=16
    for mi,(label,fn,lower_better) in enumerate(metrics):
        bx=40+mi*(CHART_W+GAP); by=panel_y
        pygame.draw.rect(surf,(20,24,42),(bx,by,CHART_W,CHART_H+50),border_radius=6)
        for li,line in enumerate(label.split('\n')):
            surf.blit(F['sml'].render(line,True,CYAN if li==0 else GRAY),(bx+6,by+4+li*16))
        vals={a:fn(ANALYZER.stats[a]) for a in ALGORITHMS}
        max_v=max(vals.values()) or 1
        bar_w=(CHART_W-16)//len(ALGORITHMS)
        for ai,a in enumerate(ALGORITHMS):
            v=vals[a]; bh2=int((v/max_v)*(CHART_H-44)) if max_v>0 else 0
            bx2=bx+8+ai*bar_w; by2=by+40; acol=algo_colors.get(a,WHITE)
            is_best=(v==min(vals.values()) if lower_better else v==max(vals.values()))
            pygame.draw.rect(surf,(30,35,55),(bx2,by2,bar_w-3,CHART_H-44),border_radius=3)
            if bh2>0: pygame.draw.rect(surf,acol,(bx2,by2+(CHART_H-44)-bh2,bar_w-3,bh2),border_radius=3)
            if is_best: pygame.draw.rect(surf,GOLD,(bx2,by2+(CHART_H-44)-bh2,bar_w-3,bh2),2,border_radius=3)
            surf.blit(F['sml'].render(a[:3],True,acol),(bx2,by2+CHART_H-42))
            vstr=f"{v:.3f}" if v<100 else f"{int(v)}"
            surf.blit(F['sml'].render(vstr,True,GOLD if is_best else GRAY),(bx2,by2+CHART_H-26))

    surf.blit(F['sml'].render("Gold border = best per metric.  Efficiency = Avg Path / Avg Nodes.",True,GRAY),(40,SCREEN_H-22))

# ══════════════════════════════════════════════
#  HUD
# ══════════════════════════════════════════════
def draw_hud(surf,fonts,t1,t2,police_list,weather,elapsed,map_name,dn,diff):
    F=fonts; pad=10
    def panel(x,y,w,h):
        s=pygame.Surface((w,h),pygame.SRCALPHA); s.fill((0,0,0,155)); surf.blit(s,(x,y))

    panel(pad,pad,215,130)
    surf.blit(F['sml'].render("PLAYER 1",True,THIEF_ORA),(pad+8,pad+3))
    surf.blit(F['big'].render(f"Score: {t1.score}",True,GOLD),(pad+8,pad+20))
    st1="ESCAPED" if t1.escaped else("CAUGHT" if not t1.alive else "Active")
    surf.blit(F['sml'].render(st1,True,GREEN if t1.escaped else(RED if not t1.alive else WHITE)),(pad+8,pad+52))
    surf.blit(F['sml'].render("WASD / Arrows",True,GRAY),(pad+8,pad+70))
    if t1.boost_timer>0: surf.blit(F['sml'].render(f"BOOST {t1.boost_timer:.1f}s",True,BOOST_COL),(pad+8,pad+90))

    panel(pad,pad+140,215,120)
    surf.blit(F['sml'].render("PLAYER 2",True,THIEF2_COL),(pad+8,pad+143))
    surf.blit(F['big'].render(f"Score: {t2.score}",True,(200,120,255)),(pad+8,pad+161))
    st2="ESCAPED" if t2.escaped else("CAUGHT" if not t2.alive else "Active")
    surf.blit(F['sml'].render(st2,True,GREEN if t2.escaped else(RED if not t2.alive else WHITE)),(pad+8,pad+193))
    surf.blit(F['sml'].render("IJKL / Numpad",True,GRAY),(pad+8,pad+211))
    if t2.boost_timer>0: surf.blit(F['sml'].render(f"BOOST {t2.boost_timer:.1f}s",True,BOOST_COL),(pad+8,pad+229))

    ph=22+len(police_list)*20+16
    panel(SCREEN_W-238,pad,228,ph)
    mins=int(elapsed)//60; secs=int(elapsed)%60
    surf.blit(F['big'].render(f"{mins:02d}:{secs:02d}",True,WHITE),(SCREEN_W-233,pad+2))
    for pi,p in enumerate(police_list):
        bc=POLICE_BADGE_COLS[p.index%len(POLICE_BADGE_COLS)]
        surf.blit(F['sml'].render(f"P{pi+1}:{p.algorithm[:8]}  cap:{p.captures}",True,bc),(SCREEN_W-233,pad+38+pi*20))
    dc={M_DEFAULT:GRAY,M_DAY:YELLOW,M_NIGHT:(100,100,255)}.get(dn,GRAY)
    surf.blit(F['sml'].render(f"{dn}|{weather}|{diff}",True,dc),(SCREEN_W-233,pad+44+len(police_list)*20))
    if any(p.is_buffed for p in police_list):
        bs=pygame.Surface((230,26),pygame.SRCALPHA); bs.fill((180,120,0,210)); surf.blit(bs,(SCREEN_W//2-115,3))
        surf.blit(F['med'].render("POLICE SPEED BUFF!",True,YELLOW),(SCREEN_W//2-95,5))
    btm=pygame.Surface((SCREEN_W,24),pygame.SRCALPHA); btm.fill((0,0,0,140)); surf.blit(btm,(0,SCREEN_H-24))
    surf.blit(F['sml'].render("P1:WASD/Arrows  P2:IJKL/Numpad  P:Pause  R:Restart  ESC:Menu  Tab:Analysis",True,GRAY),(8,SCREEN_H-18))

# ══════════════════════════════════════════════
#  MAP EDITOR
# ══════════════════════════════════════════════
class MapEditor:
    def __init__(self,fonts):
        self.EDITOR_COLS=(SCREEN_W-100)//TILE; self.EDITOR_ROWS=(SCREEN_H-100)//TILE
        self.fonts=fonts; self.grid=[[EMPTY]*self.EDITOR_COLS for _ in range(self.EDITOR_ROWS)]
        self.collectibles:Dict[Tuple,str]={}
        for c in range(self.EDITOR_COLS): self.grid[0][c]=WALL; self.grid[self.EDITOR_ROWS-1][c]=WALL
        for r in range(self.EDITOR_ROWS): self.grid[r][0]=WALL; self.grid[r][self.EDITOR_COLS-1]=WALL
        self.sel_tile=WALL; self.sel_col="tile"; self.sel_ctype=COIN; self.hovered=None
        self.OX=20; self.OY=130; self.TS=max(18,(SCREEN_W-60)//(self.EDITOR_COLS+1))

    def get_grid_and_collectibles(self):
        rows=self.EDITOR_ROWS; cols=self.EDITOR_COLS
        grid=[[EMPTY]*cols for _ in range(rows)]
        for r in range(rows):
            for c in range(cols): grid[r][c]=self.grid[r][c]
        for c in range(cols): grid[0][c]=WALL; grid[rows-1][c]=WALL
        for r in range(rows): grid[r][0]=WALL; grid[r][cols-1]=WALL
        variants=[[0]*cols for _ in range(rows)]
        colls={(r2,c2):ct for(r2,c2),ct in self.collectibles.items() if 0<=r2<rows and 0<=c2<cols}
        return grid,variants,colls

    def handle_event(self,event):
        if event.type==pygame.MOUSEBUTTONDOWN:
            mx,my=event.pos; py2=SCREEN_H-80
            for i,tp in enumerate(TILE_PALETTE):
                rx=20+i*52
                if rx<=mx<=rx+44 and py2<=my<=py2+34: self.sel_tile=tp; self.sel_col="tile"; return
            for i,ct in enumerate([COIN,NECKLACE,MONEY,GEM,BOOST]):
                rx=360+i*52
                if rx<=mx<=rx+44 and py2<=my<=py2+34: self.sel_ctype=ct; self.sel_col="collectible"; return
            if SCREEN_W-120<=mx<=SCREEN_W-20 and py2<=my<=py2+34: self._clear(); return
            gc=(mx-self.OX)//self.TS; gr=(my-self.OY)//self.TS
            if 0<=gr<self.EDITOR_ROWS and 0<=gc<self.EDITOR_COLS:
                if event.button==1:
                    if self.sel_col=="tile": self.grid[gr][gc]=self.sel_tile; self.collectibles.pop((gr,gc),None)
                    elif self.grid[gr][gc]==EMPTY: self.collectibles[(gr,gc)]=self.sel_ctype
                elif event.button==3: self.grid[gr][gc]=EMPTY; self.collectibles.pop((gr,gc),None)
        if event.type==pygame.MOUSEMOTION:
            mx,my=event.pos; gc=(mx-self.OX)//self.TS; gr=(my-self.OY)//self.TS
            self.hovered=(gr,gc) if 0<=gr<self.EDITOR_ROWS and 0<=gc<self.EDITOR_COLS else None
            if event.buttons[0] and self.hovered:
                gr2,gc2=self.hovered
                if 0<gr2<self.EDITOR_ROWS-1 and 0<gc2<self.EDITOR_COLS-1:
                    if self.sel_col=="tile": self.grid[gr2][gc2]=self.sel_tile
                    elif self.grid[gr2][gc2]==EMPTY: self.collectibles[(gr2,gc2)]=self.sel_ctype

    def _clear(self):
        self.collectibles.clear()
        for r in range(self.EDITOR_ROWS):
            for c in range(self.EDITOR_COLS):
                self.grid[r][c]=WALL if(r==0 or r==self.EDITOR_ROWS-1 or c==0 or c==self.EDITOR_COLS-1) else EMPTY

    def draw(self,surf):
        F=self.fonts; surf.fill((15,18,35))
        surf.blit(F['big'].render("MAP EDITOR — Left:paint  Right:erase  ESC:back",True,CYAN),(20,10))
        surf.blit(F['sml'].render("Paint tiles and collectibles. Select 'Custom' map then Start.",True,GRAY),(20,44))
        surf.blit(F['sml'].render("Borders are always walls. Players spawn on empty cells.",True,GRAY),(20,62))
        for r in range(self.EDITOR_ROWS):
            for c in range(self.EDITOR_COLS):
                x=self.OX+c*self.TS; y=self.OY+r*self.TS
                pygame.draw.rect(surf,TILE_COLORS.get(self.grid[r][c],(60,50,40)),(x,y,self.TS-1,self.TS-1))
                if(r,c) in self.collectibles:
                    pygame.draw.circle(surf,COLLECTIBLE_COLS[self.collectibles[(r,c)]],(x+self.TS//2,y+self.TS//2),5)
                if self.hovered==(r,c): pygame.draw.rect(surf,WHITE,(x,y,self.TS-1,self.TS-1),2)
        py2=SCREEN_H-80; surf.blit(F['sml'].render("Tiles:",True,GRAY),(20,py2-18))
        for i,tp in enumerate(TILE_PALETTE):
            rx=20+i*52; bdr=WHITE if(self.sel_col=="tile" and self.sel_tile==tp) else GRAY
            pygame.draw.rect(surf,TILE_COLORS[tp],(rx,py2,44,34),border_radius=4)
            pygame.draw.rect(surf,bdr,(rx,py2,44,34),2,border_radius=4)
            surf.blit(F['sml'].render(TILE_NAMES[tp][:4],True,WHITE),(rx+2,py2+10))
        surf.blit(F['sml'].render("Collectibles:",True,GRAY),(360,py2-18))
        for i,ct in enumerate([COIN,NECKLACE,MONEY,GEM,BOOST]):
            rx=360+i*52; bdr=WHITE if(self.sel_col=="collectible" and self.sel_ctype==ct) else GRAY
            pygame.draw.rect(surf,(30,30,50),(rx,py2,44,34),border_radius=4)
            pygame.draw.rect(surf,bdr,(rx,py2,44,34),2,border_radius=4)
            pygame.draw.circle(surf,COLLECTIBLE_COLS[ct],(rx+22,py2+17),7)
            surf.blit(F['sml'].render(ct[:4],True,WHITE),(rx+2,py2+22))
        pygame.draw.rect(surf,(120,20,20),(SCREEN_W-120,py2,100,34),border_radius=6)
        pygame.draw.rect(surf,RED,(SCREEN_W-120,py2,100,34),2,border_radius=6)
        surf.blit(F['med'].render("CLEAR",True,WHITE),(SCREEN_W-100,py2+8))

# ══════════════════════════════════════════════
#  MENU  (police count + per-officer algo)
# ══════════════════════════════════════════════
def draw_menu(surf, fonts, sel, hovered, police_algos):
    """
    Layout (1380x820):
    ┌─────────────────────────────────────────────────────────┐
    │            TITLE  /  SUBTITLE                           │
    ├──────────┬──────────┬──────────┬──────────┬────────────┤
    │  MAP     │ WEATHER  │ DAY/NGT  │  DIFF    │ # POLICE   │
    │ (col 0)  │ (col 1)  │ (col 2)  │ (col 3)  │ (col 4)   │
    ├──────────┴──────────┴──────────┴──────────┴────────────┤
    │            ALGORITHM PER OFFICER  (full width)          │
    │  Officer 1: [BFS][Dijkstra][A*][Greedy][Hill][SA][AdvA*]│
    │  …up to 5 officers                                      │
    ├──────────────────────────────────────────────────────────┤
    │ [EDIT MAP]        [Tab:Analysis hint]       [START GAME] │
    └─────────────────────────────────────────────────────────┘
    """
    F=fonts
    # Background gradient
    for y in range(SCREEN_H):
        t=y/SCREEN_H
        pygame.draw.line(surf,(int(10+35*t),int(12+30*t),int(55+75*(1-t))),(0,y),(SCREEN_W,y))

    # Title
    title=F['title'].render("AI CHASE",True,GOLD)
    sub=F['big'].render("Police vs Thief  —  AI Pathfinding Lab",True,(180,200,255))
    surf.blit(title,(SCREEN_W//2-title.get_width()//2,14))
    surf.blit(sub,(SCREEN_W//2-sub.get_width()//2,78))

    # ── Top 5-column row: MAP | WEATHER | DAY/NIGHT | DIFFICULTY | NO.POLICE ──
    # Each column gets equal width across the full screen
    COL_W   = 230          # width of each option button
    COL_GAP = (SCREEN_W - 5*COL_W) // 6   # equal gaps between & around cols
    TOP_Y   = 118          # header label y
    OPT_Y   = 140          # first option y
    OPT_H   = 32           # option button height
    OPT_GAP = 6            # gap between options

    TOP_COLS = [
        ("map",        "MAP",         MAPS,              COL_GAP + 0*(COL_W+COL_GAP)),
        ("weather",    "WEATHER",     WEATHERS,          COL_GAP + 1*(COL_W+COL_GAP)),
        ("dn",         "DAY / NIGHT", DAY_NIGHT_MODES,   COL_GAP + 2*(COL_W+COL_GAP)),
        ("diff",       "DIFFICULTY",  DIFFICULTIES,      COL_GAP + 3*(COL_W+COL_GAP)),
        ("num_police", "NO. OF POLICE", [str(n) for n in POLICE_COUNT_OPTIONS],
                                                         COL_GAP + 4*(COL_W+COL_GAP)),
    ]
    for cname,label,opts,cx in TOP_COLS:
        # Header
        htxt=F['med'].render(label,True,CYAN)
        surf.blit(htxt,(cx,TOP_Y))
        pygame.draw.line(surf,CYAN,(cx,TOP_Y+20),(cx+COL_W,TOP_Y+20),1)
        for i,opt in enumerate(opts):
            # For num_police, compare against int; others compare string
            if cname=="num_police":
                sel_b=(sel["num_police"]==POLICE_COUNT_OPTIONS[i])
            else:
                sel_b=(sel[cname]==opt)
            hov=(hovered==(cname,i))
            ry=OPT_Y+(OPT_H+OPT_GAP)*i
            bc=(50,80,160) if sel_b else((55,55,85) if hov else(22,26,50))
            bdc=GOLD if sel_b else(CYAN if hov else(60,70,110))
            pygame.draw.rect(surf,bc,(cx,ry,COL_W,OPT_H),border_radius=5)
            pygame.draw.rect(surf,bdc,(cx,ry,COL_W,OPT_H),2,border_radius=5)
            tc=GOLD if sel_b else(WHITE if hov else GRAY)
            otxt=F['med'].render(opt,True,tc)
            surf.blit(otxt,(cx+COL_W//2-otxt.get_width()//2,ry+OPT_H//2-otxt.get_height()//2))

    # ── Algorithm per officer section ─────────────────────────────────────────
    # Sits below the tallest top column (MAP has 6 items)
    max_rows = max(len(MAPS), len(WEATHERS), len(DAY_NIGHT_MODES),
                   len(DIFFICULTIES), len(POLICE_COUNT_OPTIONS))
    algo_section_y = OPT_Y + max_rows*(OPT_H+OPT_GAP) + 14

    # Section header
    pygame.draw.line(surf,(60,80,120),(20,algo_section_y-4),(SCREEN_W-20,algo_section_y-4),1)
    surf.blit(F['med'].render("ALGORITHM PER OFFICER",True,CYAN),(20,algo_section_y))

    num = sel["num_police"]
    # Each algorithm button: fit 7 algos across screen with left label
    LABEL_W = 82
    BTN_W   = (SCREEN_W - 40 - LABEL_W - 8) // len(ALGORITHMS)
    BTN_H   = 28
    ROW_GAP = 8
    for pi in range(num):
        badge = POLICE_BADGE_COLS[pi % len(POLICE_BADGE_COLS)]
        row_y = algo_section_y + 28 + pi*(BTN_H+ROW_GAP)
        # Officer label
        surf.blit(F['sml'].render(f"Officer {pi+1}",True,badge),(20,row_y+6))
        for ai,algo in enumerate(ALGORITHMS):
            bx = 20+LABEL_W+4 + ai*BTN_W
            sel_b=(police_algos[pi]==algo); hov=(hovered==('palgo',pi*10+ai))
            bc=(50,80,160) if sel_b else((40,45,70) if hov else(22,26,48))
            bdc=badge if sel_b else(CYAN if hov else(55,65,100))
            pygame.draw.rect(surf,bc,(bx,row_y,BTN_W-4,BTN_H),border_radius=4)
            pygame.draw.rect(surf,bdc,(bx,row_y,BTN_W-4,BTN_H),2,border_radius=4)
            atxt=F['sml'].render(algo,True,badge if sel_b else(WHITE if hov else GRAY))
            surf.blit(atxt,(bx+(BTN_W-4)//2-atxt.get_width()//2,row_y+BTN_H//2-atxt.get_height()//2))

    # ── Bottom action bar ──────────────────────────────────────────────────────
    ebx,eby,ebw,ebh=20,SCREEN_H-66,190,46
    eh=(hovered==('editor',0))
    pygame.draw.rect(surf,(40,60,120) if eh else(22,38,85),(ebx,eby,ebw,ebh),border_radius=8)
    pygame.draw.rect(surf,CYAN,(ebx,eby,ebw,ebh),2,border_radius=8)
    etxt=F['big'].render("EDIT MAP",True,CYAN)
    surf.blit(etxt,(ebx+ebw//2-etxt.get_width()//2,eby+10))

    sbx,sby,sbw,sbh=SCREEN_W-220,SCREEN_H-66,200,46
    sh=(hovered==('start',0))
    pygame.draw.rect(surf,(35,150,70) if sh else(22,105,48),(sbx,sby,sbw,sbh),border_radius=8)
    pygame.draw.rect(surf,GREEN,(sbx,sby,sbw,sbh),2,border_radius=8)
    stxt=F['big'].render("START GAME",True,WHITE)
    surf.blit(stxt,(sbx+sbw//2-stxt.get_width()//2,sby+10))

    hint=F['sml'].render(
        "Tab: Session Analysis   |   Custom map: use EDIT MAP first, then select Custom",
        True,(150,170,205))
    surf.blit(hint,(SCREEN_W//2-hint.get_width()//2,SCREEN_H-14))

    return (ebx,eby,ebw,ebh),(sbx,sby,sbw,sbh),TOP_COLS
def menu_hit(mx,my,eb,sb,top_cols,sel,police_algos):
    """Hit-test matches the redesigned draw_menu layout."""
    ebx,eby,ebw,ebh=eb
    if ebx<=mx<=ebx+ebw and eby<=my<=eby+ebh: return("editor",0)
    sbx,sby,sbw,sbh=sb
    if sbx<=mx<=sbx+sbw and sby<=my<=sby+sbh: return("start",0)

    # Top columns (map/weather/dn/diff/num_police)
    COL_W=230; COL_GAP=(SCREEN_W-5*COL_W)//6
    OPT_Y=140; OPT_H=32; OPT_GAP=6
    for ci,(cname,_,opts,cx) in enumerate(top_cols):
        for i in range(len(opts)):
            ry=OPT_Y+i*(OPT_H+OPT_GAP)
            if cx<=mx<=cx+COL_W and ry<=my<=ry+OPT_H: return(cname,i)

    # Algorithm per officer buttons
    max_rows=max(len(MAPS),len(WEATHERS),len(DAY_NIGHT_MODES),len(DIFFICULTIES),len(POLICE_COUNT_OPTIONS))
    algo_section_y=OPT_Y+max_rows*(OPT_H+OPT_GAP)+14
    LABEL_W=82; BTN_W=(SCREEN_W-40-LABEL_W-8)//len(ALGORITHMS); BTN_H=28; ROW_GAP=8
    num=sel["num_police"]
    for pi in range(num):
        for ai in range(len(ALGORITHMS)):
            bx=20+LABEL_W+4+ai*BTN_W; by=algo_section_y+28+pi*(BTN_H+ROW_GAP)
            if bx<=mx<=bx+BTN_W-4 and by<=my<=by+BTN_H: return("palgo",pi*10+ai)
    return None

# ══════════════════════════════════════════════
#  GAME OVER SCREEN
# ══════════════════════════════════════════════
def draw_game_over(surf,fonts,t1,t2,police_list,elapsed,particles):
    ov=pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA); ov.fill((0,0,0,185)); surf.blit(ov,(0,0))
    particles.draw(surf); F=fonts
    p1w=t1.escaped; p2w=t2.escaped; p1l=not t1.alive; p2l=not t2.alive
    if p1w and p2w:     title_txt="BOTH ESCAPED!";      title_col=GREEN
    elif p1l and p2l:   title_txt="BOTH CAPTURED!";     title_col=RED
    elif p1w and p2l:   title_txt="PLAYER 1 WINS!";     title_col=THIEF_ORA
    elif p2w and p1l:   title_txt="PLAYER 2 WINS!";     title_col=THIEF2_COL
    elif t1.score>t2.score: title_txt="P1 LEADS SCORE!"; title_col=THIEF_ORA
    elif t2.score>t1.score: title_txt="P2 LEADS SCORE!"; title_col=THIEF2_COL
    else:               title_txt="IT'S A DRAW!";        title_col=GOLD
    BW,BH=660,400; BX=SCREEN_W//2-BW//2; BY=SCREEN_H//2-BH//2
    pygame.draw.rect(surf,(20,20,38),(BX,BY,BW,BH),border_radius=14)
    pygame.draw.rect(surf,title_col,(BX,BY,BW,BH),3,border_radius=14)
    ttxt=F['title'].render(title_txt,True,title_col); surf.blit(ttxt,(SCREEN_W//2-ttxt.get_width()//2,BY+14))
    mins=int(elapsed)//60; secs=int(elapsed)%60
    total_caps=sum(p.captures for p in police_list)
    algos_used=", ".join(dict.fromkeys(p.algorithm for p in police_list))
    for i,(lbl,val,col) in enumerate([
        ("P1 Score:",str(t1.score),GOLD),("P2 Score:",str(t2.score),(200,120,255)),
        ("Time:",f"{mins:02d}:{secs:02d}",WHITE),("Officers:",str(len(police_list)),CYAN),
        ("Algorithms:",algos_used,CYAN),("Total Captures:",str(total_caps),RED),
        ("Total Nodes:",str(sum(p.nodes_explored for p in police_list)),(180,180,255))]):
        y=BY+86+i*36
        surf.blit(F['med'].render(lbl,True,GRAY),(BX+30,y)); surf.blit(F['med'].render(val,True,col),(BX+300,y))
    btns=[("PLAY AGAIN",GREEN),("SEE ANALYSIS",CYAN),("MAIN MENU",ORANGE)]
    btn_rects=[]
    for i,(txt,col) in enumerate(btns):
        rx=BX+16+i*210; ry=BY+BH-56; rw=198; rh=40
        pygame.draw.rect(surf,(20,40,20) if i==0 else(20,40,60) if i==1 else(40,20,10),(rx,ry,rw,rh),border_radius=8)
        pygame.draw.rect(surf,col,(rx,ry,rw,rh),2,border_radius=8)
        t3=F['med'].render(txt,True,col); surf.blit(t3,(rx+rw//2-t3.get_width()//2,ry+rh//2-t3.get_height()//2))
        btn_rects.append((rx,ry,rw,rh))
    for p in police_list:
        if p.captures>0: ANALYZER.record_capture(p.algorithm)
    return btn_rects

# ══════════════════════════════════════════════
#  MAIN GAME CLASS
# ══════════════════════════════════════════════
class Game:
    S_MENU="menu"; S_EDITOR="editor"; S_PLAYING="playing"
    S_PAUSED="paused"; S_GAMEOVER="gameover"
    S_ANALYSIS="analysis"; S_POSTGAME="postgame"

    def __init__(self):
        pygame.init()
        try: pygame.mixer.init(frequency=44100,size=-16,channels=2,buffer=512)
        except: pass
        self.screen=pygame.display.set_mode((SCREEN_W,SCREEN_H))
        pygame.display.set_caption("AI Chase — Police vs Thief  |  AI Lab")
        self.clock=pygame.time.Clock(); pygame.font.init()
        self.fonts={'title':pygame.font.SysFont("Arial",52,bold=True),'big':pygame.font.SysFont("Arial",28,bold=True),
                    'med':pygame.font.SysFont("Arial",20),'sml':pygame.font.SysFont("Arial",15)}
        self._init_sounds()
        self.state=self.S_MENU
        self.sel={"map":MAPS[0],"weather":SUNNY,"dn":M_DEFAULT,"diff":MEDIUM,"num_police":1}
        self.police_algos=[ASTAR,BFS,DIJKSTRA,GREEDY,HILL,SA,ADV_ASTAR]   # one per possible slot
        self.hovered=None
        self._menu_eb=None; self._menu_sb=None; self._menu_lcols=None; self._go_btn_rects=None
        self.particles=ParticleSystem(); self.weather_sys=WeatherSystem()
        self.editor=MapEditor(self.fonts)
        self.grid=None; self.variants=None; self.cols=self.rows=0; self.ox=self.oy=0
        self.t1=None; self.t2=None; self.police_list:List[Police]=[]
        self.exit_pos=None; self.collectibles:Dict[Tuple,str]={}; self.elapsed=0.0

    def _init_sounds(self):
        self.sounds={}
        try:
            sr=44100
            def tone(freq,dur,vol=0.3,wave='sine'):
                n=int(sr*dur); arr=[]
                for i in range(n):
                    tv=i/sr
                    if wave=='sine': v=math.sin(2*math.pi*freq*tv)
                    elif wave=='square': v=1.0 if math.sin(2*math.pi*freq*tv)>0 else -1.0
                    else: v=(2*(i%max(1,int(sr/freq)))/max(1,int(sr/freq)))-1
                    fade=min(1,(n-i)/max(1,int(sr*0.05)),i/max(1,int(sr*0.01)))
                    arr.append(int(v*vol*fade*32767))
                return pygame.mixer.Sound(buffer=bytes(_array.array('h',arr)))
            self.sounds['collect']=tone(880,0.12); self.sounds['escape']=tone(660,0.3)
            self.sounds['caught']=tone(200,0.4,wave='square'); self.sounds['step']=tone(300,0.05,vol=0.08)
            self.sounds['boost']=tone(1100,0.15); self.sounds['gem']=tone(1320,0.2)
        except: pass

    def sfx(self,name):
        s=self.sounds.get(name)
        if s:
            try: s.play()
            except: pass

# Star from here -------------

    def start_game(self):
        self.cols=(SCREEN_W-100)//TILE; self.rows=(SCREEN_H-100)//TILE
        self.ox=(SCREEN_W-self.cols*TILE)//2; self.oy=(SCREEN_H-self.rows*TILE)//2
        custom_colls={}
        if self.sel["map"]=="Custom":
            self.grid,self.variants,custom_colls=self.editor.get_grid_and_collectibles()
        else:
            self.grid,self.variants=generate_map(self.sel["map"],self.cols,self.rows)
        empty=[(r,c) for r in range(1,self.rows-1) for c in range(1,self.cols-1) if self.grid[r][c]==EMPTY]
        if len(empty)<4:
            self.grid,self.variants=generate_map("Forest Chase",self.cols,self.rows)
            empty=[(r,c) for r in range(1,self.rows-1) for c in range(1,self.cols-1) if self.grid[r][c]==EMPTY]
        random.shuffle(empty)
        t1pos=empty[0]; t2pos=empty[1]
        self.t1=Thief(t1pos[0],t1pos[1],1); self.t2=Thief(t2pos[0],t2pos[1],2)

        # Spawn police_list
        num=self.sel["num_police"]; self.police_list=[]; used={t1pos,t2pos}
        for pi in range(num):
            placed=False
            for ep in empty[2:]:
                if ep not in used:
                    too_close=any(_h(ep,(p.r,p.c))<6 for p in self.police_list)
                    if not too_close:
                        algo=self.police_algos[pi] if pi<len(self.police_algos) else ASTAR
                        self.police_list.append(Police(ep[0],ep[1],algorithm=algo,index=pi))
                        used.add(ep); placed=True; break
            if not placed:
                for ep in empty[2:]:
                    if ep not in used:
                        algo=self.police_algos[pi] if pi<len(self.police_algos) else ASTAR
                        self.police_list.append(Police(ep[0],ep[1],algorithm=algo,index=pi))
                        used.add(ep); break

        edge=[ep for ep in empty if ep[0]<=2 or ep[0]>=self.rows-3 or ep[1]<=2 or ep[1]>=self.cols-3]
        self.exit_pos=random.choice(edge) if edge else empty[-1]
        if custom_colls:
            self.collectibles=dict(custom_colls)
        else:
            mult=DIFF_COLLECTIBLE_MULT[self.sel["diff"]]
            ctypes=[COIN]*(30*mult)+[MONEY]*(15*mult)+[NECKLACE]*(10*mult)+[GEM]*(4*mult)
            ctypes+=[BOOST]*(6 if self.sel["diff"]==EASY else 3)
            random.shuffle(ctypes); excl=used|{self.exit_pos}; self.collectibles={}
            for ep in empty:
                if ep not in excl and ctypes: self.collectibles[ep]=ctypes.pop()
                if not ctypes: break
        self.weather_sys=WeatherSystem(self.sel["weather"])
        self.elapsed=0.0; self.particles=ParticleSystem(); self.state=self.S_PLAYING

    def handle_event(self,event):
        if self.state==self.S_EDITOR:
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: self.state=self.S_MENU; return
            self.editor.handle_event(event); return
        if self.state==self.S_ANALYSIS:
            if event.type==pygame.KEYDOWN and event.key in(pygame.K_TAB,pygame.K_ESCAPE): self.state=self.S_MENU
            return
        # Game-over popup buttons: PLAY AGAIN / SEE ANALYSIS / MAIN MENU
        if self.state==self.S_GAMEOVER:
            if event.type==pygame.KEYDOWN:
                if event.key in(pygame.K_SPACE,pygame.K_RETURN): self.start_game(); return
                if event.key in(pygame.K_m,pygame.K_ESCAPE): self.state=self.S_MENU; return
                if event.key==pygame.K_TAB: self.state=self.S_POSTGAME; return
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and self._go_btn_rects:
                mx,my=event.pos
                bx,by,bw,bh=self._go_btn_rects[0]
                if bx<=mx<=bx+bw and by<=my<=by+bh: self.start_game(); return
                bx,by,bw,bh=self._go_btn_rects[1]
                if bx<=mx<=bx+bw and by<=my<=by+bh: self.state=self.S_POSTGAME; return
                bx,by,bw,bh=self._go_btn_rects[2]
                if bx<=mx<=bx+bw and by<=my<=by+bh: self.state=self.S_MENU; return
            return

        # Post-game full analysis screen
        if self.state==self.S_POSTGAME:
            if event.type==pygame.KEYDOWN:
                if event.key in(pygame.K_SPACE,pygame.K_RETURN): self.start_game(); return
                if event.key in(pygame.K_m,pygame.K_ESCAPE): self.state=self.S_MENU; return
                if event.key==pygame.K_TAB: self.state=self.S_ANALYSIS; return
            return
        if event.type==pygame.KEYDOWN:
            k=event.key
            if k==pygame.K_ESCAPE and self.state in(self.S_PLAYING,self.S_PAUSED): self.state=self.S_MENU
            if k==pygame.K_p:
                if self.state==self.S_PLAYING: self.state=self.S_PAUSED
                elif self.state==self.S_PAUSED: self.state=self.S_PLAYING
            if k==pygame.K_r and self.state in(self.S_PLAYING,self.S_PAUSED): self.start_game()
            if k==pygame.K_TAB: self.state=self.S_ANALYSIS
        if event.type==pygame.MOUSEMOTION and self.state==self.S_MENU:
            mx,my=event.pos
            if self._menu_eb: self.hovered=menu_hit(mx,my,self._menu_eb,self._menu_sb,self._menu_lcols,self.sel,self.police_algos)
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and self.state==self.S_MENU and self._menu_eb:
            mx,my=event.pos
            hit=menu_hit(mx,my,self._menu_eb,self._menu_sb,self._menu_lcols,self.sel,self.police_algos)
            if hit:
                cname,idx=hit
                if cname=="start":    self.start_game()
                elif cname=="editor": self.state=self.S_EDITOR
                elif cname=="map":    self.sel["map"]=MAPS[idx]
                elif cname=="weather":self.sel["weather"]=WEATHERS[idx]
                elif cname=="dn":     self.sel["dn"]=DAY_NIGHT_MODES[idx]
                elif cname=="diff":   self.sel["diff"]=DIFFICULTIES[idx]
                elif cname=="num_police": self.sel["num_police"]=POLICE_COUNT_OPTIONS[idx]
                elif cname=="palgo":
                    pi=idx//10; ai=idx%10
                    if pi<len(self.police_algos) and ai<len(ALGORITHMS): self.police_algos[pi]=ALGORITHMS[ai]

    def update(self,dt):
        if self.state==self.S_GAMEOVER: self.particles.update(dt); return
        if self.state!=self.S_PLAYING: return
        self.elapsed+=dt
        keys=pygame.key.get_pressed(); ox,oy=self.ox,self.oy
        prev1=(self.t1.r,self.t1.c); self.t1.handle_input(keys,self.grid,dt); self.t1.update(dt,ox,oy)
        prev2=(self.t2.r,self.t2.c); self.t2.handle_input(keys,self.grid,dt); self.t2.update(dt,ox,oy)
        if(self.t1.r,self.t1.c)!=prev1: self.sfx('step')
        if(self.t2.r,self.t2.c)!=prev2: self.sfx('step')
        vis=self.weather_sys.visibility()
        for p in self.police_list:
            p.update(self.grid,[self.t1,self.t2],dt,vis,self.sel["dn"],self.sel["diff"])
            p.update_pixel(ox,oy,dt)
        self.weather_sys.update(dt); self.particles.update(dt)
        for thief in[self.t1,self.t2]:
            pos=(thief.r,thief.c)
            if pos in self.collectibles and thief.alive and not thief.escaped:
                ct=self.collectibles.pop(pos)
                if ct==BOOST: thief.apply_boost(); self.sfx('boost'); self.particles.emit(thief.px+ox+TILE//2,thief.py+oy+TILE//2,BOOST_COL,12,3)
                else:
                    thief.score+=COLLECTIBLE_VALUES[ct]
                    self.particles.emit(thief.px+ox+TILE//2,thief.py+oy+TILE//2,COLLECTIBLE_COLS[ct],10,3)
                    self.sfx('gem' if ct==GEM else 'collect')
        for thief in[self.t1,self.t2]:
            if(thief.r,thief.c)==self.exit_pos and thief.alive and not thief.escaped:
                thief.escaped=True; self.particles.emit(thief.px+ox+TILE//2,thief.py+oy+TILE//2,GREEN,30,5); self.sfx('escape')
        for p in self.police_list:
            for thief in[self.t1,self.t2]:
                if(p.r,p.c)==(thief.r,thief.c) and thief.alive and not thief.escaped:
                    thief.alive=False; p.captures+=1
                    self.particles.emit(p.px+TILE//2,p.py+TILE//2,RED,25,4); self.sfx('caught')
        if all((not th.alive or th.escaped) for th in[self.t1,self.t2]): self.state=self.S_GAMEOVER

    def draw(self):
        surf=self.screen; t=self.elapsed; night=(self.sel["dn"]==M_NIGHT)
        if self.state==self.S_MENU:
            eb,sb,lcols=draw_menu(surf,self.fonts,self.sel,self.hovered,self.police_algos)
            self._menu_eb=eb; self._menu_sb=sb; self._menu_lcols=lcols; pygame.display.flip(); return
        if self.state==self.S_EDITOR: self.editor.draw(surf); pygame.display.flip(); return
        if self.state==self.S_ANALYSIS: draw_analysis_screen(surf,self.fonts); pygame.display.flip(); return
        if self.state==self.S_POSTGAME:
            draw_postgame_analysis(surf,self.fonts,self.police_list,self.elapsed); pygame.display.flip(); return
        draw_sky(surf,self.sel["weather"],night)
        if self.grid:
            for r in range(self.rows):
                for c in range(self.cols): draw_tile(surf,self.grid,self.variants,r,c,self.ox,self.oy)
        if self.exit_pos: draw_exit(surf,self.exit_pos[1]*TILE+self.ox,self.exit_pos[0]*TILE+self.oy,t)
        for(r,c),ct in self.collectibles.items(): draw_collectible(surf,ct,c*TILE+self.ox,r*TILE+self.oy,t)
        for p in self.police_list:
            badge=POLICE_BADGE_COLS[p.index%len(POLICE_BADGE_COLS)]
            for i,(pr,pc) in enumerate(p.path[:6]):
                dot=pygame.Surface((8,8),pygame.SRCALPHA)
                pygame.draw.circle(dot,(*badge,max(0,180-i*30)),(4,4),4)
                surf.blit(dot,(pc*TILE+self.ox+TILE//2-4,pr*TILE+self.oy+TILE//2-4))
        if self.t1: self.t1.draw(surf)
        if self.t2: self.t2.draw(surf)
        for p in self.police_list: p.draw(surf)
        self.particles.draw(surf); self.weather_sys.draw_overlay(surf,night)
        if self.state==self.S_PLAYING and self.t1 and self.t2:
            draw_hud(surf,self.fonts,self.t1,self.t2,self.police_list,
                     self.sel["weather"],self.elapsed,self.sel["map"],self.sel["dn"],self.sel["diff"])
        if self.state==self.S_PAUSED:
            ov=pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA); ov.fill((0,0,0,130)); surf.blit(ov,(0,0))
            txt=self.fonts['title'].render("PAUSED",True,WHITE); surf.blit(txt,(SCREEN_W//2-txt.get_width()//2,SCREEN_H//2-40))
            sub=self.fonts['med'].render("P:Resume  R:Restart  ESC:Menu  Tab:Analysis",True,GRAY)
            surf.blit(sub,(SCREEN_W//2-sub.get_width()//2,SCREEN_H//2+30))
        if self.state==self.S_GAMEOVER and self.t1 and self.t2:
            if random.random()<0.25:
                self.particles.emit(random.randint(0,SCREEN_W),random.randint(80,400),random.choice([GOLD,GREEN,CYAN,WHITE]),5,2.5)
            btn_rects=draw_game_over(surf,self.fonts,self.t1,self.t2,self.police_list,self.elapsed,self.particles)
            self._go_btn_rects=btn_rects
        pygame.display.flip()

    def run(self):
        while True:
            dt=min(self.clock.tick(FPS)/1000.0,0.05)
            for event in pygame.event.get():
                if event.type==pygame.QUIT: pygame.quit(); sys.exit()
                self.handle_event(event)
            self.update(dt)
            self.draw()

if __name__=="__main__":
    Game().run()
