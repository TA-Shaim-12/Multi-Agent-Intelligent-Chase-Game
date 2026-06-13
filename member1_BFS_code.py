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
# Member 1 Dynamic Weather Handler System
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
# Procedural Layout Grid Generation Block
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