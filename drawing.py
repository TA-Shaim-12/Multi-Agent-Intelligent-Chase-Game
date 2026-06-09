def draw_sky(surf,weather,night=False): #SKY

    if night: top,bot=(5,5,20),(15,15,55) #choosing sky colors based on day/night/weather
    elif weather==STORMY: top,bot=(50,50,80),(80,80,110)
    elif weather==FOGGY: top,bot=(180,195,210),(210,220,230)
    elif weather==SNOWY: top,bot=(160,190,220),(200,215,235)
    else: top,bot=SKY_TOP,SKY_BOT

    sky_h=SCREEN_H//3 #height of sky (upper part of the screen)

    for y in range(sky_h):  #drawing gradient sky
        t=y/sky_h #t changes from 0 to 1 as y increases and is used for smooth color blending between colors
        pygame.draw.line(
            surf,
            tuple(int(top[i]*(1-t)+bot[i]*t) for i in range(3)),
            (0,y),
            (SCREEN_W,y)
        )

    if night: #night sky
        pygame.draw.circle(surf,(230,230,200),(SCREEN_W-80,55),22) #moon (two circles create glow effect)
        pygame.draw.circle(surf,(15,15,45),(SCREEN_W-68,48),18) 

        rng=random.Random(42) #drawing stars (fixed seed for same star pattern)
        for _ in range(60): #drawing 60 random star on the sky
            pygame.draw.circle(
                surf,
                (240,240,255), #star colour
                (rng.randint(0,SCREEN_W),rng.randint(0,sky_h-10)), #random star position on the sky
                rng.randint(1,2) #random star size (1/2 pixels)
            )
    elif weather==SUNNY:   #sunny weather
        pygame.draw.circle(surf,SUN_COL,(SCREEN_W-80,60),30) #drawing sun

        for a in range(0,360,30): #drawing sun rays 
            rx=int((SCREEN_W-80)+44*math.cos(math.radians(a)))
            ry=int(60+44*math.sin(math.radians(a)))
            pygame.draw.line(surf,SUN_COL,(SCREEN_W-80,60),(rx,ry),2)


def _soil(v,r,c): #soil colour generator where v=variation val, r= row, c=col,creates colour variation

    return [SOIL_DARK,SOIL_MID,SOIL_LIGHT,SOIL_MID][((r*7+c*13+v)%4)] 
    #one soil colour is chosen from list based on row, col, variation val.
    #diff pos has diff shade 
    