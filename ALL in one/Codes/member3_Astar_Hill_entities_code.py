# =============================================================
# AI CHASE GAME  -  MEMBER 3  CODE FILE
# Classes   : Thief + Police  (both player-controlled
#             and AI-controlled characters)
# Algorithms: A* (main police algo) + Hill Climbing
# Branch    : astar_[your_student_ID]
# File name : member3_Astar_Hill_entities_code.py
#
# WHAT YOU DO IN THIS FILE:
#   1. Add comments to the Thief class explaining every method
#   2. Add stun_timer mud penalty to Thief class
#      (walking on MUD slows thief to half speed for 1.5 seconds)
#   3. Add comments to the Police class explaining every method
#   4. Add stuck_timer to Police class
#      (if police does not move for 2 seconds, clear path and replan)
#   5. Create README_member3.md (200-word analysis)
#
# DO NOT edit anything outside this file.
# When done: git add, git commit, git push, open Pull Request.
# =============================================================

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