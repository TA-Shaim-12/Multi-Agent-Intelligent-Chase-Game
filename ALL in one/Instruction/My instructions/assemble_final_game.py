"""
LEADER TOOL - assemble_final_game.py
======================================
Run this script AFTER all members have pushed their notebooks.
It pulls code from each member's .ipynb file and assembles
the final runnable ai_chase_game_final.py

HOW TO USE:
  1. Clone the repo and fetch all branches
  2. Copy each member's ai_chase_game_final.ipynb into this folder
     and rename them:
       notebook_m1.ipynb  (from bfs branch)
       notebook_m2.ipynb  (from dijkstra branch)
       notebook_m3.ipynb  (from astar branch)
       notebook_m4.ipynb  (from sa branch)
       notebook_m5.ipynb  (from advastar branch - YOUR notebook)
  3. Run:  python assemble_final_game.py
  4. It produces:  ai_chase_game_ASSEMBLED.py
  5. Test it:  python ai_chase_game_ASSEMBLED.py
"""

import json, os, sys

BASE_FILE   = 'ai_chase_game_final.py'   # the 926-line base on main
OUTPUT_FILE = 'ai_chase_game_ASSEMBLED.py'

NOTEBOOKS = {
    'M1 (BFS + Foundation)':            'notebook_m1.ipynb',
    'M2 (Dijkstra + Drawing)':          'notebook_m2.ipynb',
    'M3 (A* + Entities)':               'notebook_m3.ipynb',
    'M4 (SA + UI)':                     'notebook_m4.ipynb',
    'M5 (AdvA* + Game class - YOURS)':  'notebook_m5.ipynb',
}

# Line ranges each member REPLACES in the base file (1-indexed, inclusive)
# Format: [(start, end), (start, end), ...]  multiple ranges per member
RANGES = {
    'M1 (BFS + Foundation)':           [(16, 209)],
    'M2 (Dijkstra + Drawing)':         [(211, 234), (315, 428)],
    'M3 (A* + Entities)':              [(236, 258), (430, 616)],
    'M4 (SA + UI)':                    [(260, 271), (618, 926)],
    'M5 (AdvA* + Game class - YOURS)': [(273, 313)],   # Game class appended at end
}

def extract_code_from_notebook(path):
    """Extract all code cells from a .ipynb file and join them."""
    if not os.path.exists(path):
        return None
    try:
        nb = json.load(open(path, encoding='utf-8'))
        cells = []
        for cell in nb.get('cells', []):
            if cell.get('cell_type') == 'code':
                src = ''.join(cell.get('source', []))
                if src.strip():
                    cells.append(src)
        return '\n\n'.join(cells)
    except Exception as e:
        print(f'  ERROR reading {path}: {e}')
        return None

def main():
    print('='*60)
    print('AI CHASE GAME - ASSEMBLY TOOL')
    print('='*60)

    # Load base file
    if not os.path.exists(BASE_FILE):
        print(f'ERROR: {BASE_FILE} not found in current folder.')
        print('Copy the 926-line base game file here first.')
        sys.exit(1)

    base_lines = open(BASE_FILE, encoding='utf-8').read().split('\n')
    print(f'Base file loaded: {len(base_lines)} lines')
    print()

    # Start with base lines as a list (1-indexed via [i-1])
    final_lines = list(base_lines)
    game_class_code = None

    # Process each member
    for member_name, notebook_path in NOTEBOOKS.items():
        print(f'Processing: {member_name}')

        if not os.path.exists(notebook_path):
            print(f'  SKIPPED - {notebook_path} not found')
            print(f'  Place their notebook here and re-run.')
            print()
            continue

        code = extract_code_from_notebook(notebook_path)
        if code is None:
            print(f'  FAILED to read notebook')
            print()
            continue

        member_lines = code.split('\n')
        print(f'  Extracted {len(member_lines)} lines of code')

        # For Member 5 - split their code into AdvA* part and Game class part
        if member_name.startswith('M5'):
            # Find where Game class starts in their code
            game_idx = None
            for i, l in enumerate(member_lines):
                if l.strip().startswith('class Game:'):
                    game_idx = i
                    break
            if game_idx is not None:
                adv_part  = '\n'.join(member_lines[:game_idx]).strip()
                game_class_code = '\n'.join(member_lines[game_idx:]).strip()
                member_lines = adv_part.split('\n')
                print(f'  Game class found at member code line {game_idx+1}')
                print(f'  AdvA* section: {len(member_lines)} lines')
                print(f'  Game class section: {len(game_class_code.splitlines())} lines')
            else:
                print('  WARNING: No "class Game:" found in M5 notebook.')
                print('  Make sure you have the Game class in your notebook.')

        # Replace ranges in base file
        ranges = RANGES.get(member_name, [])
        # Sort ranges in reverse so replacements do not shift indexes
        for (start, end) in sorted(ranges, reverse=True):
            # Replace lines start..end (1-indexed) with member code
            # We do a simple replacement: remove old lines, insert new
            # For simplicity, we mark them with placeholders first
            placeholder = f'# --- {member_name} CODE INSERTED HERE ---'
            final_lines[start-1:end] = [placeholder]

        print(f'  Ranges marked for replacement: {ranges}')
        print()

    # Now do the actual replacement - rebuild from scratch in correct order
    # Simpler approach: just concatenate sections in order
    print('Building final file...')

    # Load each member's code
    member_codes = {}
    for member_name, notebook_path in NOTEBOOKS.items():
        if os.path.exists(notebook_path):
            code = extract_code_from_notebook(notebook_path)
            if code:
                if member_name.startswith('M5'):
                    lines_m = code.split('\n')
                    game_idx = None
                    for i,l in enumerate(lines_m):
                        if l.strip().startswith('class Game:'):
                            game_idx = i; break
                    if game_idx:
                        member_codes[member_name] = {
                            'algo': '\n'.join(lines_m[:game_idx]),
                            'game': '\n'.join(lines_m[game_idx:])
                        }
                    else:
                        member_codes[member_name] = {'algo': code, 'game': ''}
                else:
                    member_codes[member_name] = code

    # Rebuild file section by section using base as fallback
    base = open(BASE_FILE, encoding='utf-8').read()
    base_lines = base.split('\n')
    def BL(s,e): return '\n'.join(base_lines[s-1:e])  # 1-indexed inclusive

    sections = []

    # Lines 1-15: file header (same for everyone)
    sections.append(('File header (lines 1-15)', BL(1, 15)))

    # M1: lines 16-209
    m1 = member_codes.get('M1 (BFS + Foundation)')
    sections.append(('M1 - BFS + Foundation (lines 16-209)',
                      m1 if m1 else BL(16, 209)))

    # Line 210: blank
    sections.append(('separator', BL(210, 210)))

    # M2 first range: 211-234 (Dijkstra)
    m2 = member_codes.get('M2 (Dijkstra + Drawing)')
    sections.append(('M2 - Dijkstra (lines 211-234)',
                      m2.split('\n\n')[0] if m2 else BL(211, 234)))

    # Lines 235-259: A* + Greedy + Hill (from M3 first range or base)
    m3 = member_codes.get('M3 (A* + Entities)')
    sections.append(('M3 - A*+Greedy+Hill (lines 236-258)',
                      m3.split('\n\n')[0] if m3 else BL(235, 259)))

    # Lines 260-271: SA (M4 first range)
    m4 = member_codes.get('M4 (SA + UI)')
    sections.append(('M4 - SA (lines 260-271)',
                      m4.split('\n\n')[0] if m4 else BL(260, 271)))

    # Lines 273-313: AdvA* + compute_path (M5)
    m5 = member_codes.get('M5 (AdvA* + Game class - YOURS)')
    sections.append(('M5 - AdvA* + compute_path (lines 273-313)',
                      m5['algo'] if isinstance(m5,dict) else BL(273, 313)))

    # M2 second range: 315-428 (Drawing helpers)
    sections.append(('M2 - Drawing helpers (lines 315-428)',
                      m2.split('\n\n')[1] if (m2 and '\n\n' in m2) else BL(315, 428)))

    # M3 second range: 430-616 (Analysis screens + Thief + Police classes)
    sections.append(('M3 - Thief+Police+Analysis (lines 430-616)',
                      m3.split('\n\n')[1] if (m3 and '\n\n' in m3) else BL(430, 616)))

    # M4 second range: 618-926 (HUD, MapEditor, Menu, GameOver)
    sections.append(('M4 - UI sections (lines 618-926)',
                      m4.split('\n\n')[1] if (m4 and '\n\n' in m4) else BL(618, 926)))

    # M5 Game class (appended at end)
    game_cls = ''
    if isinstance(m5, dict): game_cls = m5.get('game', '')
    if not game_cls:
        print('WARNING: Game class not found in M5 notebook.')
        print('The assembled file will NOT run without the Game class.')
        print('Check your notebook has "class Game:" and re-run.')
    sections.append(('M5 - Game class (appended after line 926)', game_cls))

    # Write output
    final = '\n\n'.join(s for _, s in sections if s.strip())

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(final)

    print()
    print('='*60)
    print(f'ASSEMBLED FILE: {OUTPUT_FILE}')
    print(f'Total lines: {len(final.splitlines())}')
    print()
    print('Sections included:')
    for name, content in sections:
        status = 'OK' if content.strip() else 'MISSING'
        print(f'  [{status}] {name}')
    print()
    print('NEXT STEP: Test the assembled file:')
    print(f'  python {OUTPUT_FILE}')
    print()
    if not game_cls:
        print('CRITICAL: Game class is missing. Game will not run.')
        print('Put your Game class in your notebook and re-run this script.')
    print('='*60)

if __name__ == '__main__':
    main()
