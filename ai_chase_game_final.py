import pygame, sys, math, random, heapq, array as _array, time
from collections import deque
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict


def adv_astar_path(grid,start,goal):
    RADIUS=18  # Defines the local search radius around the goal node.Inside this radius, Dijkstra is used to generate exact heuristic values.
    dist_map={goal:0}; pq=[(0,goal)]  # dist_map stores the shortest distance from each node to the goal. Do backward traversal.
    while pq:
        cost,node=heapq.heappop(pq)
        if cost>dist_map.get(node,1e18): continue   # Skip processing if a better path to this node already exists.
        if _h(node,goal)>RADIUS: continue           # Ignore nodes outside the predefined local radius.
        for nb in _nb(grid,node):
            new_cost=cost+_cost(grid,nb)            
            if new_cost<dist_map.get(nb,1e18):      # Update only if a shorter path is found.
                dist_map[nb]=new_cost
                heapq.heappush(pq,(new_cost,nb))
    def h_adv(pos):          # advanced heuristic function.
        return dist_map.get(pos,_h(pos,goal))   # exact if cached else Manhattan  # ── forward A* using enriched heuristic ──
    open_set=[(h_adv(start),0,start)]
    came={start:None}       # Store parent nodes for path reconstruction.
    g_cost={start:0}
    expanded=0
    while open_set:
        _,g,node=heapq.heappop(open_set)
        expanded+=1
        if node==goal:
            path=[]
            while node and node!=start:    # Backtrack from goal to start to reconstruct the path.
                path.append(node)
                node=came[node]
            return path[::-1],expanded     # reverse path to get correct order from start to goal.
        for nb in _nb(grid,node):          # Explore neighbors of the current node.
            new_g=g+_cost(grid,nb)
            if new_g<g_cost.get(nb,1e18):  # Update if a shorter route is discovered.
                g_cost[nb]=new_g
                came[nb]=node
                heapq.heappush(
                    open_set,
                    (new_g+h_adv(nb),new_g,nb)
                )
    return [],expanded






# ══════════════════════════════════════════════
#  MAIN GAME CLASS
# ══════════════════════════════════════════════

class Game:
    S_MENU = "menu"; S_EDITOR = "editor"; S_PLAYING = "playing"
    S_PAUSED = "paused"; S_GAMEOVER = "gameover"
    S_ANALYSIS = "analysis"; S_POSTGAME = "postgame"

    def __init__(self):
        pygame.init()
        try: pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)  # Initialize mixer with specific settings for better performance.
        except: pass
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H)) # Set up the main game window with defined width and height.
        pygame.display.set_caption("Multi-Agent Intelligent Chase Game") # Set the window title.
        self.clock = pygame.time.Clock(); pygame.font.init() # Create a clock object to manage the game's frame rate
        self.fonts = {'title':pygame.font.SysFont("Arial",52,bold=True),'big':pygame.font.SysFont("Arial",28,bold=True),
                    'med':pygame.font.SysFont("Arial",20),'sml':pygame.font.SysFont("Arial",15)}
        self.__init___sounds() # Load and initialize all game sounds.
        self.state = self.S_MENU # Start the game in the menu state.
        self.sel = {"map":MAPS[0],"weather":SUNNY,"dn":M_DEFAULT,"diff":MEDIUM,"num_police":1} # Default selections for map, weather, day/night cycle, difficulty, and number of police agents.
        self.police_algos = [ASTAR,BFS,DIJKSTRA,GREEDY,HILL,SA,ADV_ASTAR] # List of available algorithms for police agents.
        self.hovered = None; # Variable to track which UI element is currently hovered by the mouse.
        self._menu_eb = None; self._menu_sb = None; self._menu_lcols = None; self._go_btn_rects = None # Initialize variables for menu UI elements.
        self.particles = ParticleSystem(); self.weather_sys = WeatherSystem() # Create instances of particle system and weather system for visual effects.
        self.editor = MapEditor(self.fonts)
        self.grid = None; self.variants = None; self.cols = self.rows = 0; self.ox = self.oy=0 # Initialize variables for the game grid, variants, dimensions, and offsets.
        self.t1 = None; self.t2 = None; self.police_list:List[Police] = [] # Initialize variables for timing and list of police agents.
        self.exit_pos = None; self.collectibles:Dict[Tuple,str] = {}; self.elapsed = 0.0 # Initialize variables for exit position, collectibles, and elapsed time.

    def __init___sounds(self):
        self.sounds = {}
        try:
            sr = 44100
            def tone(freq, dur, vol=0.3, wave='sine'):
                n = int(sr*dur); arr = []
                for i in range(n):
                    tv = i/sr
                    if wave=='sine': v = math.sin(2*math.pi*freq*tv) # Generate sine wave value for the current time.
                    elif wave=='square': v=1.0 if math.sin(2*math.pi*freq*tv)>0 else -1.0 # Generate square wave value based on sine wave.
                    else: v=(2*(i%max(1,int(sr/freq)))/max(1,int(sr/freq)))-1
                    fade=min(1,(n-i)/max(1,int(sr*0.05)),i/max(1,int(sr*0.01)))
                    arr.append(int(v*vol*fade*32767))
                return pygame.mixer.Sound(buffer=bytes(_array.array('h',arr)))
        except: pass

    def sfx(self, name):
        s = self.sounds.get(name)
        if s:
            try: s.play()
            except: pass