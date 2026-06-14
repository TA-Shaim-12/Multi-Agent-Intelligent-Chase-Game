def draw_analysis_screen(surf,fonts):
    surf.fill((10,12,28)); F=fonts
    surf.blit(F['title'].render("ALGORITHM COMPARATIVE ANALYSIS",True,GOLD),(40,20))
    surf.blit(F['sml'].render("Tab/ESC: close  |  Data collected live across all game sessions",True,GRAY),(40,80))
    summary=ANALYZER.summary()
    headers=["Algorithm","Calls","Avg Time(ms)","Avg Path","Avg Nodes","Captures","Efficiency","Sol.Quality","Convergence"]
    col_x=[30,155,255,375,475,585,680,775,880]
    for i,(h,cx) in enumerate(zip(headers,col_x)):
        pygame.draw.rect(surf,(30,50,90),(cx,108,col_x[min(i+1,len(col_x)-1)]-cx-2,28),border_radius=3)
        surf.blit(F['sml'].render(h,True,CYAN),(cx+3,114))
    algo_colors={BFS:(255,200,100),DIJKSTRA:(100,220,255),ASTAR:(100,255,150),GREEDY:(255,150,100),HILL:(200,100,255),SA:(255,100,150),ADV_ASTAR:(255,255,80)}
    for ri,row in enumerate(summary):
        ry=144+ri*34; pygame.draw.rect(surf,(25,28,45) if ri%2==0 else(20,22,38),(28,ry,SCREEN_W-56,30),border_radius=3)
        vals=[row["Algorithm"],str(row["Calls"]),str(row["Avg Time (ms)"]),str(row["Avg Path Len"]),
              str(row["Avg Nodes"]),str(row["Captures"]),str(row["Efficiency"]),str(row["Sol. Quality"]),str(row["Convergence"])]
        ac=algo_colors.get(row["Algorithm"],WHITE)
        for i,(v,cx) in enumerate(zip(vals,col_x)): surf.blit(F['sml'].render(v,True,ac if i==0 else WHITE),(cx+3,ry+7))
    chart_y=360; surf.blit(F['med'].render("Execution Time (ms) — lower is better",True,CYAN),(30,chart_y))
    max_t=max((s.avg_time_ms for s in ANALYZER.stats.values()),default=1) or 1
    for i,a in enumerate(ALGORITHMS):
        s=ANALYZER.stats[a]; bx=30+i*148; by=chart_y+28; col=algo_colors.get(a,WHITE)
        bh=int((s.avg_time_ms/max_t)*90) if max_t>0 else 0
        pygame.draw.rect(surf,(28,32,52),(bx,by,138,105),border_radius=4)
        if bh>0: pygame.draw.rect(surf,col,(bx+4,by+101-bh,130,bh),border_radius=3)
        surf.blit(F['sml'].render(a[:10],True,col),(bx+3,by+106)); surf.blit(F['sml'].render(f"{s.avg_time_ms:.4f}ms",True,GRAY),(bx+3,by+122))
    chart_y2=520; surf.blit(F['med'].render("Nodes Expanded — lower = more efficient",True,CYAN),(30,chart_y2))
    max_n=max((s.avg_nodes for s in ANALYZER.stats.values()),default=1) or 1
    for i,a in enumerate(ALGORITHMS):
        s=ANALYZER.stats[a]; bx=30+i*148; by=chart_y2+28; col=algo_colors.get(a,WHITE)
        bh=int((s.avg_nodes/max_n)*90) if max_n>0 else 0
        pygame.draw.rect(surf,(28,32,52),(bx,by,138,100),border_radius=4)
        if bh>0: pygame.draw.rect(surf,col,(bx+4,by+96-bh,130,bh),border_radius=3)
        surf.blit(F['sml'].render(a[:10],True,col),(bx+3,by+98)); surf.blit(F['sml'].render(f"{s.avg_nodes:.0f} nodes",True,GRAY),(bx+3,by+114))
    surf.blit(F['sml'].render("Efficiency=PathLen/Nodes  |  Sol.Quality=Efficiency×100  |  Convergence=avg ms of last 10 calls",True,GRAY),(30,SCREEN_H-24))

