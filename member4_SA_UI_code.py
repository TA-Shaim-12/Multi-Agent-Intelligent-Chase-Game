import math
import random
#-------------------------------------- PART_1: Algorithm: Simulated Annealing------------------------------------------

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


# --------------------------------Task 2: Algorithm tooltips for draw_menu function--------------------------------------
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

#-----------------------------------Task 4: MVP officer display for game over screen-------------------------------------
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

# ---------------------------Task 5: Save and load custom map for MapEditor-------------------------------------

def save_map_editor_data(editor, fname="custom_map.json"):
    # Import json to convert map data into JSON format
    import json

    # Import pathlib to write file easily using Path
    import pathlib

    # Prepare map data with grid and collectibles
    # Tuple keys are converted into string because JSON cannot store tuple keys directly
    data = {
        "grid": editor.grid,
        "colls": {
            str(k): v
            for k, v in editor.collectibles.items()
        }
    }

    # Save the map data into a JSON file
    pathlib.Path(fname).write_text(json.dumps(data))


def load_map_editor_data(editor, fname="custom_map.json"):
    # Import json to read saved JSON map data
    import json

    # Import pathlib to check and read file path
    import pathlib

    # Create path object for the saved map file
    p = pathlib.Path(fname)

    # Load map only if the file exists
    if p.exists():

        # Read JSON data from file
        d = json.loads(p.read_text())

        # Restore saved grid data
        editor.grid = d["grid"]

        # Convert string keys back into tuple keys for collectibles
        editor.collectibles = {
            eval(k): v
            for k, v in d["colls"].items()
        }