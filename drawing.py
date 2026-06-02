def draw_sky(surf,weather,night=False): #SKY

    if night: top,bot=(5,5,20),(15,15,55) #choosing sky colors based on day/night/weather
    elif weather==STORMY: top,bot=(50,50,80),(80,80,110)
    elif weather==FOGGY: top,bot=(180,195,210),(210,220,230)
    elif weather==SNOWY: top,bot=(160,190,220),(200,215,235)
    else: top,bot=SKY_TOP,SKY_BOT

    # Height of sky area (upper part of screen)
    sky_h=SCREEN_H//3