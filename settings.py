import pickle
from tkinter import *
try:
    open('.vira_config')
except:
    pickle.dump([1920, 1080, 1], open('.vira_config', 'wb'))
vals = pickle.load(open('.vira_config', 'rb'))
names = ['output x size', 'output y size', 'frames per second multiplier']
def update():
    global CLIP_X, CLIP_Y, FPS
    CLIP_X, CLIP_Y, FPS = vals
def load():
    global CLIP_X, CLIP_Y, FPS, vals
    vals = [CLIP_X, CLIP_Y, FPS]
    pickle.dump(vals, open('.vira_config', 'wb'))
update()
def show_window():
    root = Tk()
    root.title('preview&export settings')
    entrys = []
    texts = []
    for val in range(len(names)):
        c = Canvas(root, width=200, height=20)
        c.pack()
        c.create_text(100, 10, text=names[val])
        v = StringVar(root, value=vals[val])
        e = Entry(root, textvariable=v)
        e.pack()
        entrys.append(e)
        texts.append(v)
    def update_all(evt):
        for e in range(len(entrys)):
            try:
                vals[e] = int(entrys[e].get())
            except:
                texts[e].set('')
        pickle.dump(vals, open('.vira_config', 'wb'))
        update()
    root.bind('<Key>', update_all)
    while True:
        try:
            root.update()
        except:#_tkinter.TclError
            break
