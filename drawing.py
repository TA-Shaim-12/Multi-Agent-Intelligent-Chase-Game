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
    
def _soil(v,r,c): # soil color generator (it creates variation so that the ground doesn't look repetitive)
    return [SOIL_DARK,SOIL_MID,SOIL_LIGHT,SOIL_MID][((r*7+c*13+v)%4)]


def draw_tile(surf,grid,variants,r,c,ox,oy):

    x=ox+c*TILE  # converting grid position into screen position
    y=oy+r*TILE

    t=grid[r][c] # getting tile type and variation value
    v=variants[r][c]

    
    base=_soil(v,r,c) # drawing soil color
    pygame.draw.rect(surf,base,(x,y,TILE,TILE))

    for i in range(3): # adding small dots for soil texture
        dark=tuple(max(0,base[j]-20) for j in range(3))
        pygame.draw.circle(
            surf,
            dark,
            (x+(c*17+i*11+v*5)%TILE,y+(r*13+i*7+v*3)%TILE), 2
        )

    if t==EMPTY:  # stop drawing if tile is empty
        return

    cx2,cy2=x+TILE//2,y+TILE//2 # center point of tile (used for placing objects)

    if t==BUSH: #drawing bush
        for dx2,dy2,r2,col in[
            (-6,4,10,BUSH_DARK),(6,4,10,BUSH_DARK), # darker circles for shadow effect
            (0,-2,12,BUSH_MID),(-8,0,9,BUSH_MID),(8,0,9,BUSH_MID), # main bush body
            (0,-6,8,BUSH_LITE),(-4,-4,6,BUSH_LITE),(4,-4,6,BUSH_LITE) # lighter circles to create highlights
        ]: # drawing multiple circles to form a bush where each tuple contains (x offset, y offset, radius, color)
            pygame.draw.circle(surf,col,(cx2+dx2,cy2+dy2),r2)

    elif t==STONE: #drawing stone
        c1=(100+v*8,100+v*5,95+v*6) # base stone shape (two overlapping ellipses c1,c2)
        c2=(140+v*6,138+v*5,130+v*4) # 'v' changes the colors slightly so every stone looks different

        pygame.draw.ellipse(surf,c1,(x+4,y+6,TILE-8,TILE-10)) # drawing the larger base ellipse 
        pygame.draw.ellipse(surf,c2,(x+8,y+8,TILE-16,TILE-16)) # drawing a smaller lighter ellipse to make the stone look 3D

        if v % 2 == 0: # small crack line for variation
            pygame.draw.line(surf,(70,68,65),(cx2-5,cy2-3),(cx2+3,cy2+5),1)

        pygame.draw.line(surf,(80,80,75),(cx2-6,cy2-2),(cx2+4,cy2+4),2) # drawing main shadow line to create depth


    elif t==MUD: #drawing mud
        pygame.draw.rect(surf,MUD_COL,(x+2,y+2,TILE-4,TILE-4)) # drawing muddy ground using dark brown rectangle

        for i in range(4): # adding random mud spots to give surface texture
            pygame.draw.ellipse(
                surf,
                (60,40,20), # modulus is used so the spots stay inside the tile
                (x+5+(c*11+i*9)%(TILE-10), # x position of mud spot 
                 y+5+(r*7+i*11)%(TILE-10), # y position of mud spot
                 6,4) #width and height of mud spot 
            )


    elif t==TREE: #drawing tree
        pygame.draw.rect(surf,(80,50,20),(cx2-3,cy2,6,14)) # drawing tree trunk

        pygame.draw.ellipse(surf,(50,40,25),(cx2-8,cy2+12,16,6)) # drawing shadow under trunk to give grounded effect

        for dx2,dy2,r2,col in[ # drawing multiple circles for tree leaves (x offset, y offset, radius, color)
            (0,-4,14,(20,90,15)), # main leaves (dark green)
            (-5,-2,10,(30,110,20)), # left side leaves (medium green)
            (4,-6,9,(50,140,35)), # right side leaves (bright green)
            (0,-10,7,(70,160,55)) # top leaves (light green)
        ]:
            pygame.draw.circle(surf,col,(cx2+dx2,cy2+dy2),r2) # drawing each leaf circle for tree center

    elif t==WALL: #drawing wall
        pygame.draw.rect(surf,(80,75,70),(x+1,y+1,TILE-2,TILE-2)) # drawing outer wall block slightly padded for visibility

        # Brick pattern inside wall
        for brow in range(2):  # creating brick pattern inside the wall where the wall is divided into rows and columns of bricks (iterates through brick rows)
            for bcol in range(2+brow%2): # alternates num of bricks each row to create staggered brick wall effect
                bx2=x+1+bcol*((TILE-2)//(2+brow%2)) # calculates brick position
                by2=y+1+brow*((TILE-2)//2) 
                bw2=(TILE-2)//(2+brow%2)-2 # calculates brick sixe
                bh2=(TILE-2)//2-2

                pygame.draw.rect(surf,(100,95,90),(bx2,by2,bw2,bh2)) # drawing brick body
                pygame.draw.rect(surf,(65,60,55),(bx2,by2,bw2,bh2),1) # drawing darker outline around each brick so they are noticable

def draw_collectible(surf,ctype,x,y,t): #drawing collectoibles(gem, money coin etc)

    cx2,cy2=x+TILE//2,y+TILE//2 # finding center position of the tile
    bob=int(4*math.sin(t*3)) # creating a bobbing animation
    col=COLLECTIBLE_COLS[ctype] # getting color assigned for the collectible type

    if ctype==COIN: #drawing coin
        pygame.draw.circle(surf,col,(cx2,cy2+bob),9) #drawing main coin circle (gold)
        pygame.draw.circle(surf,WHITE,(cx2-3,cy2-3+bob),3) #drawing shine effect for highlighting the coin
        pygame.draw.circle(surf,(180,140,0),(cx2,cy2+bob),9,2) #drawing outer borderfor depth and visibility

    elif ctype==NECKLACE: #drawing necklace
        for i in range(8): #drawing small beads using loop to create necklace shape
            a=i*math.pi/4 #bead placement angle
            pygame.draw.circle( #drawing individual necklace beads
                surf,
                col,
                (cx2+int(9*math.cos(a)),cy2+int(5*math.sin(a))+bob),
                3
            )
        pygame.draw.circle(surf,(200,180,250),(cx2,cy2+bob),4) #drawing jewwl/gem in the middle

    elif ctype==MONEY: #drawing money 
        pygame.draw.rect(surf,col,(cx2-9,cy2-6+bob,18,13),border_radius=3) #drawing note body
        pygame.draw.rect(surf,(20,150,50),(cx2-9,cy2-6+bob,18,13),2,border_radius=3) #drawing border around note for visibility
        fs=pygame.font.SysFont("Arial",9,bold=True) #small font for dollar sign
        surf.blit(fs.render("$",True,(20,150,50)),(cx2-4,cy2-5+bob)) #drawing '$' sign in the center

    elif ctype==GEM: #drawing gem
        pts=[(cx2,cy2-11+bob),(cx2+7,cy2-3+bob),(cx2+5,cy2+7+bob), 
             (cx2-5,cy2+7+bob),(cx2-7,cy2-3+bob)] # points used to create a gem shape
        pygame.draw.polygon(surf,col,pts) # drawing filled polygon for gem body
        pygame.draw.polygon(surf,WHITE,pts,1) #drawing white line to make the edge look clearer
        pygame.draw.line(surf,WHITE,(cx2,cy2-11+bob),(cx2,cy2+7+bob),1) #drawing center highlight line for crystal effect

    elif ctype==BOOST: #drawing boost 
        glow=abs(math.sin(t*4))*0.5+0.5 #drawing glow animation that changes brightness over time, giving boost item energy effect
        c2=tuple(int(BOOST_COL[i]*glow) for i in range(3)) # adjusting boost color brightness dynamically

        pts=[(cx2,cy2-11+bob),(cx2+5,cy2-2+bob),(cx2+1,cy2-2+bob),
             (cx2+6,cy2+9+bob),(cx2-1,cy2+1+bob),(cx2+3,cy2+1+bob)] # drawing lightning bolt style points for boost icon

        pygame.draw.polygon(surf,c2,pts) #drawing glowing lightning bolt for boost 
        pygame.draw.polygon(surf,WHITE,pts,1) #drawing white border for visibility

def draw_exit(surf,x,y,t): #drawing exit

    glow=abs(math.sin(t*2))*80 #pulsing glow effect
    col=(50,int(200+glow/2),int(100+glow/2))  #changes green/blue intensity based on glow, so exit becomes brighter and darker

    pygame.draw.rect(surf,col,(x+2,y+2,TILE-4,TILE-4),border_radius=6) #drawing main exit tile with rounded corners with small padding inside
    pygame.draw.rect(surf,WHITE,(x+2,y+2,TILE-4,TILE-4),2,border_radius=6) #drawing white border around exit tile for visibility

    fs=pygame.font.SysFont("Arial",11,bold=True) # creating small bold font
    txt=fs.render("EXIT",True,WHITE)  #writes "EXIT" in white

    surf.blit(txt,(x+TILE//2-txt.get_width()//2,
                   y+TILE//2-txt.get_height()//2)) # drawing EXIT text at the center of the tile by adjusting height and width based on text size
                   

def draw_character(surf,x,y,is_police,direction,anim_frame,captured=False,body_col=None,badge_col=None): #drawing character

    if body_col is None: #use blue for police and orange for thief if there's no body color
        body_col=POLICE_BLUE if is_police else THIEF_ORA

    if badge_col is None: #use gold for police and red for thief if there's no badge color
        badge_col=GOLD if is_police else (180,30,30)

    skin=(220,175,130) #skin color used for face and hands

    cx2,cy2=x+TILE//2,y+TILE//2 #finding center of the character based on tile position

    ls=int(7*math.sin(anim_frame*math.pi*2)) #creating smooth leg movment
        #this value continuously changes to simulate walking.
   
    pygame.draw.line(  #drawing left leg
        surf,
        (50,50,80),
        (cx2-5,cy2+8),
        (cx2-5+ls,cy2+20),
        4
    )

    pygame.draw.line( #drawing right leg
        surf,
        (50,50,80),
        (cx2+5,cy2+8),
        (cx2+5-ls,cy2+20),
        4
    )

    pygame.draw.ellipse( #drawing left foot
        surf,
        (30,25,20),
        (cx2-9+ls,cy2+17,8,5)
    )

    pygame.draw.ellipse( #drawing right foot
        surf,
        (30,25,20),
        (cx2+1-ls,cy2+17,8,5)
    )

    pygame.draw.rect( #drawing the main body as a rectangle with rounded corners
        surf,
        body_col,
        (cx2-10,cy2-4,20,16),
        border_radius=4
    )

    pygame.draw.circle( #drawing badge in the middle of the body
        surf,
        badge_col,
        (cx2,cy2+3),
        4
    )

    asw=int(5*math.sin(anim_frame*math.pi*2+math.pi)) #animating arm movement
    #here, arms move opposite to legs and to make it happen, adding 'pi' which shifts the movement direction

    pygame.draw.line( #drawing left arm
        surf,
        body_col,
        (cx2-10,cy2-2),
        (cx2-16,cy2+8+asw),
        4
    )

    pygame.draw.line( #drawing right arm
        surf,
        body_col,
        (cx2+10,cy2-2),
        (cx2+16,cy2+8-asw),
        4
    )

    pygame.draw.circle( #drawing left hand
        surf,
        skin,
        (cx2-16,cy2+8+asw),
        4
    )

    pygame.draw.circle( #drawing right hand
        surf,
        skin,
        (cx2+16,cy2+8-asw),
        4
    )

    pygame.draw.rect( #drawing neck 
        surf,
        skin,
        (cx2-4,cy2-8,8,8)
    )

    pygame.draw.circle( #drawing head as a circle
        surf,
        skin,
        (cx2,cy2-14),
        12
    )

    # adding accessories based on character type 
    if is_police: #drawing police cap

        pygame.draw.rect( #drawing bottom of the cap as a rectangle with rounded corners
            surf,
            POLICE_BLUE,
            (cx2-13,cy2-22,26,8),
            border_radius=3
        )

        pygame.draw.rect( #drawing top of the cap as a small rectangle with rounded corners
            surf,
            (20,40,140),
            (cx2-10,cy2-26,20,7),
            border_radius=3
        )

        pygame.draw.circle( #drawing badge on the cap
            surf,
            badge_col,
            (cx2,cy2-22),
            3
        )

    else:
        hair=(40,30,20) if body_col==THIEF_ORA else (80,10,120) #changing hair color depending on thief type

        pygame.draw.ellipse( #drawing hair 
            surf,
            hair,
            (cx2-11,cy2-26,22,12)
        )

        band=(180,30,30) if body_col==THIEF_ORA else (120,20,180) #giving different color to headband based on thief type

        pygame.draw.rect( #drawing headband
            surf,
            band,
            (cx2-11,cy2-20,22,5),
            border_radius=2
        )


    ex=4 if direction==0 else(-4 if direction==1 else 0) #eye direction, 0=right, 1=left, else=forward

    pygame.draw.circle(surf,BLACK,(cx2+ex-3,cy2-16),2) #drawing left eye

    pygame.draw.circle(surf,BLACK,(cx2+ex+3,cy2-16),2) #drawing right eye

    pygame.draw.circle(surf,WHITE,(cx2+ex-3,cy2-16),1) #drawing small white circle for shine effect on left eye

    pygame.draw.circle(surf,WHITE,(cx2+ex+3,cy2-16),1) #drawing small white circle for shine effect on right eye


    if captured: #drawing capture effect, when character is captured draw a red X over character

        pygame.draw.line( #drawing first diagonal line of X
            surf,
            RED,
            (cx2-14,cy2-28),
            (cx2+14,cy2+22),
            3
        )

        pygame.draw.line( #drawing second diagonal line of X
            surf,
            RED,
            (cx2+14,cy2-28),
            (cx2-14,cy2+22),
            3
        )