from micro import * #import micro won't work, no functions can be called from the library but whith this they can
init(width=300, height=300, title='test') #size and other perameters of the game window
while True:
    update(target_fps=60)#sets fps, needs to be called on regularly

    if key('R') >1: #if pressed for more than one frame
        clear(color='red') #clears game window to red

    if key('B') >1:
        clear(color='blue')

    if key('G') >1:
        clear(color='lime') #lime is true 0,255,0 green, regular'green is darker'

    if key('Z') > 1:
        quit()
        break #stops micro and breaks the loop, if there were just quit() then it would close for 1 frame and then reappear

    if key('E') >1:
        fill_rectangle(width=100, height=100, x=0, y=0, color='black') #location is from the center, colors are css based
