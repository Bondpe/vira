import time, pickle
try:
    open('.vira_config')
except:
    pickle.dump([1920, 1080, 30], open('.vira_config', 'wb'))
vals = pickle.load(open('.vira_config', 'rb'))
names = ['output x size', 'output y size', 'frames per second']
def update():
    global CLIP_X, CLIP_Y, FPS
    CLIP_X, CLIP_Y, FPS = vals
    FPS = 25 # due to bug, after that bug is fixed, we will remove this
update()
selectedVal = 0
def show_window(Window):
    global currentVal, selectedVal
    prefs = Window(500, 500, '#aba')
    nums = '123456789'
    currentVal = vals[selectedVal]
    class NumReact:
        def __init__(self, num):
            self.num = num
        def press(self):
            global currentVal
            currentVal *= 10
            currentVal += int(self.num)
            time.sleep(0.125)
    for x in nums:
        prefs.bind(NumReact(x).press, int(x)+9)
    prefs.bind(NumReact('0').press, 19)
    def earase():
        global currentVal
        currentVal = currentVal//10
        time.sleep(0.125)
    prefs.bind(earase, 22)
    def click(x, y):
        global selectedVal, currentVal
        n = (y-10)//20
        if n < len(vals) and n >= 0:
            selectedVal = n
            currentVal = vals[selectedVal]
    prefs.create_clicker(0, 0, 500, 500, click)
    while True:
        prefs.canvas.create_rectangle(0, selectedVal*20+10, 500, selectedVal*20+30, fill='#aaa')
        for tid in range(len(vals)):
            prefs.canvas.create_text(250, tid*20+20, text=names[tid]+': '+str(vals[tid]))
        vals[selectedVal] = currentVal
        prefs.update()
        update()
        pickle.dump(vals, open('.vira_config', 'wb'))
