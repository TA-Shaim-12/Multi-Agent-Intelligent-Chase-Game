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

    def __init___sounds(self):  # Load and initialize sound effects for the game.
        self.sounds = {}
        try:
            sr = 44100 
            def tone(freq, dur, vol=0.3, wave='sine'): # Generate a sound effect of a specific frequency, duration, volume, and waveform type.
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


 # Initialize the game state for a new play session based on the current selections and map configuration.
    def start_game(self):
        self.cols = (SCREEN_W-100)//TILE; self.rows = (SCREEN_H-100)//TILE 
        self.ox = (SCREEN_W-self.cols*TILE)//2; self.oy = (SCREEN_H-self.rows*TILE)//2
        custom_colls = {}
        if self.sel["map"] == "Custom":  # If the selected map is "Custom", load the grid and collectibles from the map editor.
            self.grid,self.variants,custom_colls = self.editor.get_grid_and_collectibles() # Retrieve the custom map defined in the map editor.
        else: # generate the grid and variants based on the selected map name and dimensions.
            self.grid,self.variants = generate_map(self.sel["map"],self.cols,self.rows)
        empty = [(r,c) for r in range(1,self.rows-1) for c in range(1,self.cols-1) if self.grid[r][c]==EMPTY]
        if len(empty)<4: # Ensure there are enough empty tiles to place the thieves and police agents.
            self.grid,self.variants = generate_map("Forest Chase",self.cols,self.rows)
            empty=[(r,c) for r in range(1,self.rows-1) for c in range(1,self.cols-1) if self.grid[r][c]==EMPTY]
        random.shuffle(empty) 
        t1pos=empty[0]; t2pos=empty[1] # Randomly select starting positions for the two thieves from the list of empty tiles on the grid.
        self.t1=Thief(t1pos[0],t1pos[1],1); self.t2=Thief(t2pos[0],t2pos[1],2)

        # Spawn police_list
        num = self.sel["num_police"]; self.police_list = []; used={t1pos,t2pos} # tracking the police's spawned position
        for pi in range(num): # Placing the police in the map while ensuring not to spawn close to the thieves or each other.
            placed = False
            for ep in empty[2:]: 
                if ep not in used:
                    too_close = any(_h(ep,(p.r,p.c))<6 for p in self.police_list)
                    if not too_close:
                        algo=self.police_algos[pi] if pi<len(self.police_algos) else ASTAR
                        self.police_list.append(Police(ep[0],ep[1],algorithm=algo,index=pi))
                        used.add(ep); placed = True; break
            if not placed:
                for ep in empty[2:]:
                    if ep not in used:
                        algo=self.police_algos[pi] if pi<len(self.police_algos) else ASTAR
                        self.police_list.append(Police(ep[0],ep[1],algorithm=algo,index=pi))
                        used.add(ep); break

        edge = [ep for ep in empty if ep[0] <= 2 or ep[0] >= self.rows-3 or ep[1] <= 2 or ep[1] >= self.cols-3] # Identify edge tiles for potential exit positions, ensuring they are not too close to the center of the grid.
        self.exit_pos = random.choice(edge) if edge else empty[-1] # Randomly select the exit point.
        if custom_colls:
            self.collectibles=dict(custom_colls)
        else:
            mult = DIFF_COLLECTIBLE_MULT[self.sel["diff"]]
            ctypes = [COIN]*(30*mult)+[MONEY]*(15*mult)+[NECKLACE]*(10*mult)+[GEM]*(4*mult)
            ctypes += [BOOST]*(6 if self.sel["diff"]==EASY else 3)
            random.shuffle(ctypes); excl = used|{self.exit_pos}; self.collectibles={}
            for ep in empty:
                if ep not in excl and ctypes: self.collectibles[ep]=ctypes.pop()
                if not ctypes: break
        self.weather_sys = WeatherSystem(self.sel["weather"])  #Weather selection for the game.
        self.elapsed = 0.0; self.particles=ParticleSystem(); self.state=self.S_PLAYING #set the game state to playing.


    def handle_event(self, event):   # Handle user inpput and help navigate between different game states (menu, editor, analysis, game over, post-game analysis).
        if self.state==self.S_EDITOR: # if in edditor mode, pass the event to the editor for handling.
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: self.state=self.S_MENU; return
            self.editor.handle_event(event); return
        if self.state==self.S_ANALYSIS:
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: self.state=self.S_MENU; return
            return
        if self.state==self.S_GAMEOVER: # Game-over popup buttons(Play Again, Analysis, Main Menu) handling.
            if event.type==pygame.KEYDOWN: # keyboard shortcuts keys.
                if event.key in(pygame.K_SPACE,pygame.K_RETURN): self.start_game(); return
                if event.key in(pygame.K_m,pygame.K_ESCAPE): self.state=self.S_MENU; return
                if event.key==pygame.K_TAB: self.state=self.S_POSTGAME; return
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and self._go_btn_rects:  # Check mouse click on screen.
                mx,my=event.pos
                bx,by,bw,bh=self._go_btn_rects[0]
                if bx<=mx<=bx+bw and by<=my<=by+bh: self.start_game(); return
                bx,by,bw,bh=self._go_btn_rects[1]
                if bx<=mx<=bx+bw and by<=my<=by+bh: self.state=self.S_POSTGAME; return
                bx,by,bw,bh=self._go_btn_rects[2]
                if bx<=mx<=bx+bw and by<=my<=by+bh: self.state=self.S_MENU; return
            return
        
        if self.state==self.S_POSTGAME:  # Post game analysis screen.
            if event.type==pygame.KEYDOWN:  
                if event.key in(pygame.K_SPACE,pygame.K_RETURN): self.start_game(); return
                if event.key in(pygame.K_m,pygame.K_ESCAPE): self.state=self.S_MENU; return
                if event.key==pygame.K_TAB: self.state=self.S_ANALYSIS; return
            return
        if event.type==pygame.KEYDOWN: # keyboard shortcuts keys.  
            k=event.key
            if k==pygame.K_ESCAPE and self.state in(self.S_PLAYING,self.S_PAUSED): self.state=self.S_MENU
            if k==pygame.K_p:
                if self.state==self.S_PLAYING: self.state=self.S_PAUSED
                elif self.state==self.S_PAUSED: self.state=self.S_PLAYING
            if k==pygame.K_r and self.state in(self.S_PLAYING,self.S_PAUSED): self.start_game()
            if k==pygame.K_TAB: self.state=self.S_ANALYSIS
        if event.type==pygame.MOUSEMOTION and self.state==self.S_MENU:  # update hovered menu item based on mouse position.
            mx,my=event.pos
            if self._menu_eb: self.hovered=menu_hit(mx,my,self._menu_eb,self._menu_sb,self._menu_lcols,self.sel,self.police_algos)
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and self.state==self.S_MENU and self._menu_eb:  # handle mouse click on menu items.
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


    def update(self, dt): # Update game state based on current state.
        if self.state==self.S_GAMEOVER: self.particles.update(dt); return
        if self.state!=self.S_PLAYING: return # Only update game logic if in playing state.
        self.elapsed+=dt  
        keys=pygame.key.get_pressed(); ox,oy=self.ox,self.oy  # Store original offsets for calculating movement and particle effects.
        prev1=(self.t1.r,self.t1.c); self.t1.handle_input(keys,self.grid,dt); self.t1.update(dt,ox,oy)
        prev2=(self.t2.r,self.t2.c); self.t2.handle_input(keys,self.grid,dt); self.t2.update(dt,ox,oy)
        if(self.t1.r,self.t1.c)!=prev1: self.sfx('step')  # Play step sound effect.
        if(self.t2.r,self.t2.c)!=prev2: self.sfx('step')
        vis=self.weather_sys.visibility()
        for p in self.police_list:  #  Police's state update based on selection.
            p.update(self.grid,[self.t1,self.t2],dt,vis,self.sel["dn"],self.sel["diff"])
            p.update_pixel(ox,oy,dt)
        self.weather_sys.update(dt); self.particles.update(dt)
        for thief in[self.t1,self.t2]:  # Add effects and sound when a thief collects an item.
            pos=(thief.r,thief.c) 
            if pos in self.collectibles and thief.alive and not thief.escaped:
                ct=self.collectibles.pop(pos)
                if ct==BOOST: thief.apply_boost(); self.sfx('boost'); self.particles.emit(thief.px+ox+TILE//2,thief.py+oy+TILE//2,BOOST_COL,12,3)
                else:
                    thief.score+=COLLECTIBLE_VALUES[ct]
                    self.particles.emit(thief.px+ox+TILE//2,thief.py+oy+TILE//2,COLLECTIBLE_COLS[ct],10,3)
                    self.sfx('gem' if ct==GEM else 'collect')
        for thief in[self.t1,self.t2]:  # Check if the thief reaches the exit or gets caught by the police.
            if(thief.r,thief.c)==self.exit_pos and thief.alive and not thief.escaped:
                thief.escaped=True; self.particles.emit(thief.px+ox+TILE//2,thief.py+oy+TILE//2,GREEN,30,5); self.sfx('escape')
        for p in self.police_list:  # Check if any police catches a theif.
            for thief in[self.t1,self.t2]:
                if(p.r,p.c)==(thief.r,thief.c) and thief.alive and not thief.escaped:
                    thief.alive=False; p.captures+=1
                    self.particles.emit(p.px+TILE//2,p.py+TILE//2,RED,25,4); self.sfx('caught')
        if all((not th.alive or th.escaped) for th in[self.t1,self.t2]): self.state=self.S_GAMEOVER