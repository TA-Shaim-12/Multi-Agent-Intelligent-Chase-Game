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

# This dictionary explains each algorithm shortly for the menu tooltip.
# When the user hovers over an algorithm button, the matching text is shown.
ALGO_TIPS = {
    "BFS": "Shortest hops, ignores terrain cost",
    "Dijkstra": "Cheapest real cost, terrain-aware",
    "A*": "Cost plus heuristic, optimal and fast",
    "Greedy": "Beelines to goal, not optimal",
    "Hill Climbing": "Local search, can get stuck",
    "Sim. Annealing": "Probabilistic, explores diversely",
    "Adv A*": "Dijkstra-enriched heuristic, best paths",
}


def draw_algorithm_tooltip(surf, F, hovered, ALGORITHMS, CYAN, SCREEN_W, SCREEN_H):
    # Check whether the hovered item is an algorithm button
    if isinstance(hovered, tuple) and hovered[0] == "palgo":

        # Extract algorithm index from hovered value
        ai = hovered[1] % 10

        # Make sure the index is inside the algorithm list
        if ai < len(ALGORITHMS):

            # Get tooltip text for the selected algorithm
            tip = ALGO_TIPS.get(ALGORITHMS[ai], "")

            # Draw the tooltip text at the bottom center of the menu screen
            surf.blit(
                F["sml"].render(tip, True, CYAN),
                (SCREEN_W // 2 - 200, SCREEN_H - 36)
            )




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