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

#--------------------------------------Task 3: Mini scoreboard for HUD------------------------------------------

def draw_mini_scoreboard(surf, F, t1, t2, SCREEN_W, SCREEN_H,
                         THIEF_ORA, THIEF2_COL, GOLD):
    # Compare Player 1 and Player 2 scores
    # This section decides who is leading the match

    if t1.score > t2.score:
        # Player 1 is leading
        leader = f"P1 leads +{t1.score - t2.score}"

        # Use Player 1 thief color for the lead text
        lead_col = THIEF_ORA

    elif t2.score > t1.score:
        # Player 2 is leading
        leader = f"P2 leads +{t2.score - t1.score}"

        # Use Player 2 thief color for the lead text
        lead_col = THIEF2_COL

    else:
        # Both players have equal score
        leader = "Tied!"

        # Use gold color when the game is tied
        lead_col = GOLD

    # Draw the mini scoreboard at the bottom center of the screen
    surf.blit(
        F["sml"].render(leader, True, lead_col),
        (SCREEN_W // 2 - 60, SCREEN_H - 24)
    )


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