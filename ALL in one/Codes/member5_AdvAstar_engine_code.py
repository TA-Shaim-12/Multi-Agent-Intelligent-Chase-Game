# =============================================================
# AI CHASE GAME  -  MEMBER 5  CODE FILE  (LEADER)
# Algorithms: Simulated Annealing + Advanced A* (MANDATORY)
#             + compute_path dispatcher
# Section   : Full Game class (engine, events, update, draw)
# Branch    : advastar_[your_student_ID]
# File name : member5_AdvAstar_engine_code.py
#
# WHAT YOU DO IN THIS FILE:
#   PART A - YOUR ALGORITHMS (top section):
#   1. Add comments to EVERY line of sa_path() explaining
#      T, cooling schedule, acceptance probability, fallback
#   2. Add comments to EVERY line of adv_astar_path() explaining
#      Phase 1 (backward Dijkstra), Phase 2 (forward A*),
#      why RADIUS=18, why it is still admissible/optimal
#   3. Add timing warning to compute_path() - warn if >50ms
#
#   PART B - GAME CLASS (bottom section):
#   4. Add Hard mode 120-second time limit in update()
#   5. Add F5 screenshot shortcut in handle_event()
#   6. Add verdict line to draw_postgame_analysis() calls
#   7. Create README_member5.md (600-word full analysis)
#
# DO NOT edit anything outside this file.
# When done: git add, git commit, git push, open Pull Request.
# =============================================================

# =============================================================
# PART A  -  YOUR ALGORITHMS
# (SA + Advanced A* + compute_path)
# Lines 260-315 of the full game file
# =============================================================

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


# =============================================================
# PART B  -  GAME CLASS
# (Game engine - init, start, events, update, draw, run)
# Lines 931-1171 of the full game file
# =============================================================

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