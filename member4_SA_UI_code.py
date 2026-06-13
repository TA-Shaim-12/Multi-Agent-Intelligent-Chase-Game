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

def draw_mvp_officer(surf, F, police_list, POLICE_BADGE_COLS, BX, BY, BH):
    # Check if there is at least one police officer in the game
    if police_list:

        # Find the officer with the highest number of captures
        mvp = max(police_list, key=lambda p: p.captures)

        # Show MVP only if the officer has at least one capture
        if mvp.captures > 0:

            # Select badge color based on officer index
            bc = POLICE_BADGE_COLS[mvp.index % len(POLICE_BADGE_COLS)]

            # Prepare MVP message with officer number, algorithm, and captures
            mvp_text = (
                f"MVP: Officer {mvp.index + 1} ({mvp.algorithm})"
                f" - {mvp.captures} capture(s)"
            )

            # Draw MVP information near the bottom of game over panel
            surf.blit(
                F["med"].render(mvp_text, True, bc),
                (BX + 30, BY + BH - 90)
            )


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