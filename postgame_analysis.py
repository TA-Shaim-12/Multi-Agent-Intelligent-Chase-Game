def draw_postgame_analysis(surf, fonts, police_list, elapsed):
    surf.fill((8,10,24)); F=fonts
    surf.blit(F['title'].render("POST-GAME  ALGORITHM  ANALYSIS",True,GOLD),(40,18))
    surf.blit(F['sml'].render(
        f"Duration: {int(elapsed)//60:02d}:{int(elapsed)%60:02d}  |  Officers: {len(police_list)}  |  "
        "SPACE/Enter=Play Again   M=Menu   Tab=Session Stats", True,GRAY),(40,74))

    algo_colors={BFS:(255,200,100),DIJKSTRA:(100,220,255),ASTAR:(100,255,150),GREEDY:(255,150,100),HILL:(200,100,255),SA:(255,100,150),ADV_ASTAR:(255,255,80)}

    # ── Officer table ──
    headers=["Officer","Algorithm","Captures","Nodes Used","Avg Path Len","Efficiency"]
    col_x=[40,130,300,410,550,660]
    surf.blit(F['med'].render("Officer Performance This Game",True,CYAN),(40,108))
    for i,(h,cx) in enumerate(zip(headers,col_x)):
        nxt=col_x[min(i+1,len(col_x)-1)]
        pygame.draw.rect(surf,(30,50,90),(cx,130,nxt-cx-2,26),border_radius=3)
        surf.blit(F['sml'].render(h,True,WHITE),(cx+4,136))
    for ri,p in enumerate(police_list):
        ry=162+ri*30; bc=POLICE_BADGE_COLS[p.index%len(POLICE_BADGE_COLS)]
        pygame.draw.rect(surf,(22,26,42) if ri%2==0 else(18,21,36),(38,ry,690,26),border_radius=3)
        ac=algo_colors.get(p.algorithm,WHITE)
        avg_path=round(ANALYZER.stats[p.algorithm].avg_path_len,1)
        eff=ANALYZER.stats[p.algorithm].efficiency
        for val,cx in zip([f"Officer {ri+1}",p.algorithm,str(p.captures),str(p.nodes_explored),str(avg_path),str(eff)],col_x):
            surf.blit(F['sml'].render(val,True,bc if cx==40 else(ac if cx==130 else WHITE)),(cx+4,ry+6))

    # ── 4-metric bar charts ──
    panel_y=162+len(police_list)*30+24
    surf.blit(F['med'].render("Algorithm Comparative Metrics  (session totals)",True,CYAN),(40,panel_y))
    metrics=[
        ("Execution Time (ms)\nlower=faster",        lambda s:s.avg_time_ms,       True),
        ("Solution Quality\nhigher=better path",      lambda s:s.solution_quality,  False),
        ("Efficiency  path/nodes\nhigher=smarter",    lambda s:s.efficiency,        False),
        ("Convergence  last-10 avg ms\nlower=stable", lambda s:float(sum(s.convergence_log[-10:])/max(len(s.convergence_log[-10:]),1)) if s.convergence_log else 0, True),
    ]
    panel_y+=28; CHART_W=310; CHART_H=110; GAP=16
    for mi,(label,fn,lower_better) in enumerate(metrics):
        bx=40+mi*(CHART_W+GAP); by=panel_y
        pygame.draw.rect(surf,(20,24,42),(bx,by,CHART_W,CHART_H+50),border_radius=6)
        for li,line in enumerate(label.split('\n')):
            surf.blit(F['sml'].render(line,True,CYAN if li==0 else GRAY),(bx+6,by+4+li*16))
        vals={a:fn(ANALYZER.stats[a]) for a in ALGORITHMS}
        max_v=max(vals.values()) or 1
        bar_w=(CHART_W-16)//len(ALGORITHMS)
        for ai,a in enumerate(ALGORITHMS):
            v=vals[a]; bh2=int((v/max_v)*(CHART_H-44)) if max_v>0 else 0
            bx2=bx+8+ai*bar_w; by2=by+40; acol=algo_colors.get(a,WHITE)
            is_best=(v==min(vals.values()) if lower_better else v==max(vals.values()))
            pygame.draw.rect(surf,(30,35,55),(bx2,by2,bar_w-3,CHART_H-44),border_radius=3)
            if bh2>0: pygame.draw.rect(surf,acol,(bx2,by2+(CHART_H-44)-bh2,bar_w-3,bh2),border_radius=3)
            if is_best: pygame.draw.rect(surf,GOLD,(bx2,by2+(CHART_H-44)-bh2,bar_w-3,bh2),2,border_radius=3)
            surf.blit(F['sml'].render(a[:3],True,acol),(bx2,by2+CHART_H-42))
            vstr=f"{v:.3f}" if v<100 else f"{int(v)}"
            surf.blit(F['sml'].render(vstr,True,GOLD if is_best else GRAY),(bx2,by2+CHART_H-26))

    surf.blit(F['sml'].render("Gold border = best per metric.  Efficiency = Avg Path / Avg Nodes.",True,GRAY),(40,SCREEN_H-22))
