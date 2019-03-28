#!/usr/env/python3
import sys, effects, settings, random, loadEffect
import interfaceBase as If
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk, ImageShow, ImageDraw, ImageFilter
# ---------------------------------Create window
from window import Window
editor = Window(1400, 800, '#000')
version='0.1.2'
editor.tk.title('vira v'+version)
generatePreview = False
RGBHSV=(None, None, None, None, None, None)
XY = 0,0
mask_points = []
mask_path = None
mask_blur = 0
selected_mask_point = None
mask_last_x,mask_last_y = 0,0
creating_mask = False
# ---------------------------------Initialise functions
loadEffect.main(effects, editor, filedialog)

def refreshPreview():
        global generatePreview
        generatePreview = True


editor.create_clicker(400, 780, 440, 800, refreshPreview)


# ============================ File
projectPath = None

show_settings = lambda: settings.show_window(Window)

editor.bind(show_settings, 37, 30)

def newVideo():
    global projectPath
    If.new()
    effects.applied_effects = []
    projectPath = None
    editor.tk.title('vira v'+version)
    refreshPreview()


editor.bind(newVideo, 37, 57)


def openVideo():
    global projectPath
    path = filedialog.Open(editor.tk).show()
    if path == () or path == '':
        return
    try:
        effects.applied_effects = If.openF(path)
        projectPath = path
        editor.tk.title('vira v'+version+' - '+path)
    except:
        If.videos.append(If.Video(path))
    refreshPreview()


editor.bind(openVideo, 37, 32)


def saveAsVideo():
    global projectPath
    path = filedialog.SaveAs(editor.tk).show()
    If.save(path, effects.applied_effects)
    projectPath = path
    editor.tk.title('vira v'+version+' - '+path)


editor.bind(saveAsVideo, 37, 50, 39)


def saveVideo():
    global projectPath
    if projectPath is None:
        saveAsVideo()
    else:
        If.save(projectPath, effects.applied_effects)


editor.bind(saveVideo, 37, 39)


def showStreamerHelp():
    win = Window(500, 450)
    win.tk.title('help - streamer')
    win.create_button(230, 420, 270, 440, win.tk.destroy, 'OK')
    win.bind(win.tk.destroy, 36)
    win.create_text(250, 25, 'VIRA', size=25, fill='#fa0')
    win.create_text(250, 70, 'simple video editor for raspberrypi', size=20, fill='green')
    win.create_text(250, 100, 'streamer', size=20, fill='blue')
    win.create_down_menu(0, 0, 50, 15, 'Stream', [
                        'Change start', 'Cut start', 'Cut duration'], [None, None, None])
    win.create_text(250, 250, '''
For moving in time and cropping videos, there
is a thing called "streamer", located on the
bottom of editor. Selected stream is defined
by blue rectangle around. You can move stream
with arrow keys, crop with Ctrl or Shift and
arrows. To add new video file, just press
Shift+A or use Edit>add. to delete, use red
cross button under streamer, to move video
between streams, click on blue 3 down-arrows
button. Also, select another stream by
clicking on its rectangle. If you're working
with bigger number of steams, just click on
'scale' button and enter percents. To do cutting
and moving more precisely, use Stream menu.
Also, scroll down the streamer with green arrows
under streams. Orange circular arrow there updates
preview. Green right and left arrows and "frame"
button - horizontal streamer navigation''', size=10)
    while True:
        try:
            win.update()
        except:
                break


def showSaveHelp():
    win = Window(500, 700)
    win.tk.title('help - saving')
    win.create_button(230, 670, 270, 690, win.tk.destroy, 'OK')
    win.bind(win.tk.destroy, 36)
    win.create_text(250, 25, 'VIRA', size=25, fill='#fa0')
    win.create_text(250, 70, 'simple video editor for raspberrypi', size=20, fill='green')
    win.create_text(250, 100, 'saving, packing,', size=20, fill='blue')
    win.create_text(250, 120, 'opening and exporting', size=20, fill='blue')
    win.create_down_menu(0, 0, 30, 15, 'File',
                         ['New', 'Open', 'Save', 'Save as', 'Help', 'Quit'], [None, None, None, None, None, None])
    win.create_down_menu(30, 0, 60, 15, 'Edit', ['Add', 'Export', 'Pack'], [None, None, None])
    win.create_text(250, 450, '''using File menu, you can save your project,
but using edit you may pack it.
the difference:
    saved file contains LINKS to video files,
    so after files are deleted editor will show
    error and stop loading file

    packed file contains BINARY DATA of videos
    it means that this file is independent

you open these files the same way, with file menu

to export something onto video file so any video
editor can play them,
select Edit>Export, then select folder and file.
EXTENSIONS ARE IMPORTANT. Using them ffmpeg defines
container type and codec. If not selected with
extension, ffmpeg generates no output file.
After that editor will start exporting. it requires
A LOT of cpu power. There is even a risk of
overheating while analysing really big videos.
Wait until editor unfreezes, then find your file!
UNUSEFUL CLONES OF FILE and EDIT MENUS ARE ON TOP OF THE WINDOW''', size=10)
    while True:
        try:
            win.update()
        except:
                break


def showEffectsHelp():
    win = Window(500, 250)
    win.tk.title('help - effects')
    win.create_button(230, 220, 270, 240, win.tk.destroy, 'OK')
    win.bind(win.tk.destroy, 36)
    win.create_text(250, 25, 'VIRA', size=25, fill='#fa0')
    win.create_text(250, 70, 'simple video editor for raspberrypi', size=20, fill='green')
    win.create_text(250, 100, 'creating visual effects', size=20, fill='blue')
    win.create_text(250, 150, '''
To add effect, press on "add effect" on the right and enter input values. Effect
is added to selected stream only. To see streams effects, select it. To change
effects input value, click on that value shown. To cut effect, click on
effects name. to delete it, click on red cross. Blue arrows move effect
between streams. Too many effects are forbidden, autoremoving last one.
Also, they're showing in streamer as thin lines, but only for current stream.''', size=10)
    while True:
        try:
            win.update()
        except:
                break


def showHelp():
    win = Window(500, 700)
    win.tk.title('help')
    win.create_button(230, 670, 270, 690, win.tk.destroy, 'OK')
    win.bind(win.tk.destroy, 36)
    win.create_text(250, 25, 'VIRA', size=25, fill='#fa0')
    win.create_text(250, 60, 'simple video editor for raspberrypi', size=10, fill='green')
    win.create_text(250, 80, 'hopefully, it works on any linux', size=10)
    win.create_text(250, 95, 'install requirements:', size=15, fill='blue')
    win.create_rectangle(0, 105, 500, 125, fill='#aaa')
    win.create_text(200, 115, '# apt install python3-pil imagemagick ffmpeg python3-tk zenity', size=10)
    win.create_text(150, 135, 'more help here:', size=10)
    def showStreamerHelpD():
        win.tk.destroy()
        showStreamerHelp()
    win.create_button(0, 150, 500, 175, showStreamerHelpD, 'basic video cutting')
    def showSaveHelpD():
        win.tk.destroy()
        showSaveHelp()
    win.create_button(0, 200, 500, 225, showSaveHelpD, 'saving, exporting and packing')
    def showEffectsHelpD():
        win.tk.destroy()
        showEffectsHelp()
    win.create_button(0, 250, 500, 275, showEffectsHelpD, 'effects')
    while True:
        try:
            win.update()
        except:
                break


editor.bind(showHelp, 37, 43)
editor.bind(showHelp, 67)


def exq():
    editor.tk.destroy()
    sys.exit()


editor.bind(exq, 37, 24)


# ============================ Edit


def Add():
    path = filedialog.Open(editor.tk).show()
    if path == () or path == '':
        return
    If.videos.append(If.Video(path))
    refreshPreview()
    return


editor.bind(Add, 50, 38)


def export():
    path = filedialog.SaveAs(editor.tk).show()
    d = simpledialog.SimpleDialog(editor.tk,
                 text="Warning: turbo mode is much faster, "
                      "but power-consuming, memory-consuming, "
                      "you can easily loose data, and there is a "
                      "risk of overheating while using it",
                 buttons=["Turbo mode", "Normal mode", "Cancel"],
                 default=1,
                 cancel=2,
                 title="Export mode")
    mode = d.go()
    if mode == 2:
        return
    If.export(path, effects, (mode == 0))


editor.bind(export, 37, 26)


def pack():
    path = filedialog.SaveAs(editor.tk).show()
    If.pack(path, effects.applied_effects)


editor.bind(pack, 37, 33)


# ============================ Stream
selected_stream = 1
streamerPos = 0


def change_start():
    global selected_stream, streamerPos
    stream = selected_stream+streamerPos-1
    if len(If.videos) <= stream:
        return
    start = simpledialog.askinteger(
        "Change stream data (start)",
        "stream starts playing from environment frame\n(%s):" %
        If.videos[stream].path, initialvalue=0) - 1
    If.videos[stream].start = start
    refreshPreview()


def frame_right():
    """move current stream one frame right"""
    global selected_stream, streamerPos
    stream = selected_stream+streamerPos-1
    If.videos[stream].start += 1
    refreshPreview()


editor.bind(frame_right, 114)


def frame_left():
    """move current stream one frame left"""
    global selected_stream, streamerPos
    stream = selected_stream+streamerPos-1
    If.videos[stream].start -= 1
    refreshPreview()


editor.bind(frame_left, 113)


def end_right():
    """move current stream end one frame right"""
    global selected_stream, streamerPos
    stream = selected_stream+streamerPos-1
    If.videos[stream].durationF += 1
    refreshPreview()


editor.bind(end_right, 37, 114)


def end_left():
    """move current stream end frame one frame left"""
    global selected_stream, streamerPos
    stream = selected_stream+streamerPos-1
    If.videos[stream].durationF -= 1
    refreshPreview()


editor.bind(end_left, 37, 113)


def from_right():
    """move current stream playFrom one frame right"""
    global selected_stream, streamerPos
    stream = selected_stream+streamerPos-1
    If.videos[stream].fromF += 1
    frame_right()
    refreshPreview()


editor.bind(from_right, 50, 114)


def from_left():
    """move current stream playFrom one frame left"""
    global selected_stream, streamerPos
    stream = selected_stream+streamerPos-1
    If.videos[stream].fromF -= 1
    frame_left()
    refreshPreview()


editor.bind(from_left, 50, 113)


def change_from():
    global selected_stream, streamerPos
    stream = selected_stream+streamerPos-1
    if len(If.videos) <= stream:
        return
    start = simpledialog.askinteger(
        "Change stream data (start)", "stream start at self-frame\n(%s):" %
        If.videos[stream].path, initialvalue=0) - 1
    If.videos[stream].fromF = start
    refreshPreview()


def change_len():
    global selected_stream, streamerPos
    stream = selected_stream+streamerPos-1
    if len(If.videos) <= stream:
        return
    start = simpledialog.askinteger(
        "Change stream data (start)", "streams last frame\n(%s):" %
        If.videos[stream].path, initialvalue=0)-1
    If.videos[stream].durationF = start+If.videos[stream].start
    refreshPreview()


def change_transparency():
    global selected_stream
    stream = selected_stream+streamerPos-1
    if len(If.videos) <= stream:
        return
    percent = simpledialog.askinteger(
        "Change stream data (transparency)", "streams transparency\n(%s):" %
        If.videos[stream].path, initialvalue=0)-1
    if percent < 0 or percent > 100:
        return
    If.videos[stream].transparency = percent/100
    If.videos[stream].mask = None
    refreshPreview()


def create_mask():
    global selected_stream, mask_points, creating_mask, mask_last_x, mask_last_y
    mask_points = []
    mask_last_x,mask_last_y = XY[0], XY[1]
    creating_mask = True


def update_mask():
    global selected_stream, mask_points, creating_mask, mask_last_x, mask_last_y, mask_path, selected_mask_point, mask_blur
    if mask_last_x == XY[0] and mask_last_y == XY[1]:
        return
    if selected_mask_point is not None:
        mask_points[selected_mask_point] = XY
        mask_last_x,mask_last_y = XY[0], XY[1]
        im = Image.new("RGB", (If.clip_size_Y, If.clip_size_X))
        draw = ImageDraw.Draw(im)
        draw.polygon(mask_points,fill=(255,255,255))
        stream = selected_stream+streamerPos-1
        im = im.filter(ImageFilter.GaussianBlur(radius=mask_blur))
        id = mask_path
        im.save('mask%d.png'%id)
        If.videos[stream].mask = 'mask%d.png'%id
        refreshPreview()
        selected_mask_point = None
        return
    if not creating_mask:
        for i in range(len(mask_points)):
            if round(XY[0]/10) == round(mask_points[i][0]/10) and round(XY[1]/10) == round(mask_points[i][1]/10):
                selected_mask_point = i
                mask_last_x,mask_last_y = XY[0], XY[1]
                return
    if len(mask_points) >= 3 and round(XY[0]/10) == round(mask_points[0][0]/10) and round(XY[1]/10) == round(mask_points[0][1]/10):
        print('saved mask')
        im = Image.new("RGB", (If.clip_size_Y, If.clip_size_X))
        draw = ImageDraw.Draw(im)
        draw.polygon(mask_points,fill=(255,255,255))
        stream = selected_stream+streamerPos-1
        mask_blur = simpledialog.askinteger(
                "Border of that mask", "mask border sharpness\n(%s):" %
                If.videos[stream].path, initialvalue=0)
        im = im.filter(ImageFilter.GaussianBlur(radius=mask_blur))
        id = random.randint(0, 100000)
        im.save('mask%d.png'%id)
        If.videos[stream].mask = 'mask%d.png'%id
        creating_mask = False
        mask_path = id
        refreshPreview()
    else:
        print('added point')
        mask_points.append(XY)
        mask_last_x,mask_last_y = XY[0], XY[1]


# ~~preview
previewImage = None
previewFrame = 1
oldPreviewFe = 1
streamerScale = 1
streamerFrame = 0


def newPreview():
    global previewFrame
    previewFrame = (editor.mouse[0]-200-streamerFrame*streamerScale)/streamerScale
    if previewFrame < 0:
        previewFrame = 0


editor.create_clicker(200, 600, 1200, 780, newPreview)
# ~~streams
# scale


def newScale():
    global streamerScale
    streamerScale = simpledialog.askinteger("Streamer", "New scale (%)")/100


editor.create_clicker(160, 780, 200, 800, newScale)
# pos


def newFramePos():
    global streamerFrame
    streamerFrame = simpledialog.askinteger("Streamer", "Skip to frame")


def streamerButtonRight():
    global streamerFrame
    streamerFrame -= 1


def streamerButtonLeft():
    global streamerFrame
    streamerFrame += 1


editor.create_clicker(440, 780, 480, 800, newFramePos)
editor.create_clicker(480, 780, 520, 800, streamerButtonLeft)
editor.create_clicker(520, 780, 560, 800, streamerButtonRight)


def newPos():
    global streamerPos
    streamerPos = simpledialog.askinteger("Streamer", "New segment")-1


def streamerButtonUp():
    global streamerPos
    streamerPos -= 1


def streamerButtonDown():
    global streamerPos
    streamerPos += 1


editor.create_clicker(200, 780, 240, 800, newPos)
editor.create_clicker(240, 780, 280, 800, streamerButtonUp)
editor.create_clicker(280, 780, 320, 800, streamerButtonDown)


def removeCurrentStream():
    global selected_stream
    if selected_stream > len(If.videos):
        return
    del If.videos[selected_stream-1]
    todel = []
    for x in range(len(effects.applied_effects)):
        if selected_stream == effects.applied_effects[x].stream:
            todel.append(x)
    for x in todel:
        del effects.applied_effects[x]
    for x in range(len(effects.applied_effects)):
        if selected_stream-1 < effects.applied_effects[x].stream:
            effects.applied_effects[x].stream -= 1
    refreshPreview()


editor.create_clicker(320, 780, 360, 800, removeCurrentStream)
editor.bind(removeCurrentStream, 119)


def stream_down():
    global selected_stream
    if selected_stream > len(If.videos):
        return
    a = If.videos[selected_stream-1]
    del If.videos[selected_stream-1]
    If.videos.insert(selected_stream, a)
    refreshPreview()


editor.create_clicker(360, 780, 400, 800, stream_down)


for n in range(9):
    exec('''def set_selected():
    global selected_stream, streamerPos
    selected_stream = %d+streamerPos
editor.create_clicker(150, 600+n*20, 1200, 620+n*20, set_selected)''' %
         (n + 1))


# -------effects
editor.create_rectangle(0, 100, 200, 600, fill='#baa')

effectFuncs = []
for name in effects.names:
    exec('''
global effectFuncs
def fun():
    effects.apply(%s)
    n = 0
    for val in effects.applied_effects[-1].vals:
        if effects.applied_effects[-1].vt[n] == 'float':
            effects.applied_effects[-1].data[val] = simpledialog.askfloat(
            "Add image effect", val, initialvalue=1)
        elif effects.applied_effects[-1].vt[n] == 'str':
            effects.applied_effects[-1].data[val] = simpledialog.askstring(
            "Add image effect", val, initialvalue=1)
        elif effects.applied_effects[-1].vt[n] == 'file':
            effects.applied_effects[-1].data[val] = filedialog.Open(editor.tk).show()
        elif effects.applied_effects[-1].vt[n] == 'hue':
            if RGBHSV[3] is not None:
                effects.applied_effects[-1].data[val] = RGBHSV[3]
            else:
                effects.applied_effects[-1].data[val] = simpledialog.askfloat(
                "Add image effect", val, initialvalue=0)
        elif effects.applied_effects[-1].vt[n] == 'saturation':
            if RGBHSV[4] is not None:
                effects.applied_effects[-1].data[val] = RGBHSV[4]
            else:
                effects.applied_effects[-1].data[val] = simpledialog.askfloat(
                "Add image effect", val, initialvalue=100)
        elif effects.applied_effects[-1].vt[n] == 'value':
            if RGBHSV[5] is not None:
                effects.applied_effects[-1].data[val] = RGBHSV[5]
            else:
                effects.applied_effects[-1].data[val] = simpledialog.askfloat(
                "Add image effect", val, initialvalue=255)
        n += 1
    effects.applied_effects[-1].stream = selected_stream
    refreshPreview()
effectFuncs.append(fun)''' % ('"'+name+'"'))

editor.create_down_menu(1200, 0, 1400, 15, 'add effect', effects.names, effectFuncs)
editor.create_text(100, 107, 'Effects', fill='#555')
visible_effects = []


def remove_effect(x_click, y_click):
    global visible_effects
    for y, n in visible_effects:
        if y < y_click and y+40 > y_click:
            del effects.applied_effects[n]
    refreshPreview()


editor.create_clicker(170, 100, 200, 600, remove_effect)


def change_stream_effect(x_click, y_click):
    global visible_effects
    for y, n in visible_effects:
        if y < y_click and y+20 > y_click:
            effects.applied_effects[n].stream -= 1
            if effects.applied_effects[n].stream < 1:
                effects.applied_effects[n].stream = 1
        if y+20 < y_click and y+40 > y_click:
            effects.applied_effects[n].stream += 1
    refreshPreview()


editor.create_clicker(0, 100, 30, 600, change_stream_effect)


def edit_effect(x_click, y_click):
    global visible_effects
    for y, n in visible_effects:
        if y+40 < y_click and \
        y+len(effects.applied_effects[n].vals)*20+40 > y_click:
            value = effects.applied_effects[n].vals[(y_click-y-40)//20]
            value_type = effects.applied_effects[n].vt[(y_click-y-40)//20]
            if value_type == 'float':
                effects.applied_effects[n].data[value] = simpledialog.askfloat(
                    "Edit image effect", value,
                    initialvalue=effects.applied_effects[n].data[value])
            elif value_type == 'str':
                effects.applied_effects[n].data[value] = simpledialog.askstring(
                    "Edit image effect", value,
                    initialvalue=effects.applied_effects[n].data[value])
            elif value_type == 'file':
                effects.applied_effects[n].data[value] = filedialog.Open(editor.tk).show()
        if y < y_click and y+40 > y_click:
            val = simpledialog.askinteger(
                "effect start", "choose new begin frame",
                initialvalue=effects.applied_effects[n].start)
            if val == None:
                return
            if val >= 0:
                effects.applied_effects[n].start = val
            val = simpledialog.askinteger(
                "effect duration", "choose new duration in frames\nCancel - forever",
                initialvalue=effects.applied_effects[n].duration)
            if val == None:
                effects.applied_effects[n].duration = -1
            if val >= 0:
                effects.applied_effects[n].duration = val
    refreshPreview()



editor.create_clicker(30, 100, 170, 600, edit_effect)

# ------end

colourpickerTextId=editor.create_text(700, 50, '')
def pick_colour(x,y):
    global RGBHSV, XY
    if previewImage:
        img = Image.open('/tmp/vira/prew.gif')
        xS,yS=img.size
        xP=int((x-200)/1000*xS)
        yP=int((y-100)/500*yS)
        r,g,b = img.convert('RGB').load()[xP,yP]
        h,s,v = img.convert('HSV').load()[xP,yP]
        editor.change_object(colourpickerTextId, [700, 50, 'x: %d, y: %d, r: %d, g: %d, b: %d, h: %d, s: %d, v: %d'%(xP,yP,r,g,b,h,s,v), ('Ariel', 5), 'orange'])
        RGBHSV=(r,g,b,h,s,v)
        XY = xP, yP
editor.create_clicker(200, 100, 1200, 600, pick_colour)

editor.create_down_menu(0, 0, 30, 15, 'File',
                        ['New',   'Open',    'Save',    'Save as',    'Preferences', 'Help',   'Quit'],
                        [newVideo, openVideo, saveVideo, saveAsVideo, show_settings, showHelp, exq])
editor.create_down_menu(30, 0, 60, 15, 'Edit', [
                        'Add', 'Export', 'Pack'], [Add, export, pack])
editor.create_down_menu(60, 0, 110, 15, 'Stream', [
                        'Change start', 'Cut start', 'Cut duration', 'Enter transparency', 'Draw mask'],
                        [change_start,   change_from, change_len, change_transparency, create_mask])

while True:
    update_mask()
    If.clip_size_X, If.clip_size_Y = settings.CLIP_X, settings.CLIP_Y
    if streamerPos < 0:
        streamerPos = 0
    # streamer area fill
    editor.canvas.create_rectangle(200, 600, 1200, 800, fill='#eee')
    editor.canvas.create_rectangle(160, 600, 200, 800, fill='#aaa')

    # display streams
    p, n = 0, 0
    if selected_stream*20 > streamerPos*20:
        editor.canvas.create_rectangle(
                150, 580+selected_stream*20-streamerPos*20,
                1200, 600+selected_stream*20-streamerPos*20, fill='#00d')
    for video in If.videos:
        n = p-streamerPos*20
        if n >= 0:
            editor.canvas.create_rectangle(
                200, 600+n, 1200, 620+n, fill='#ddd')
            e1 = (video.start - video.fromF) * streamerScale + streamerFrame*streamerScale
            if e1 < 0:
                e1 = 0
            if e1 > 1000:
                e1 = 1000
            e2 = (video.start - video.fromF + video.len) * streamerScale + streamerFrame*streamerScale
            if e2 < 0:
                e2 = 0
            if e2 > 1000:
                e2 = 1000
            editor.canvas.create_rectangle(200 + e1, 600+n,
                                           200 + e2, 620+n, fill='#ffa')
            e1 = video.start * streamerScale + streamerFrame*streamerScale
            if e1 < 0:
                e1 = 0
            if e1 > 1000:
                e1 = 1000
            e2 = (video.start - video.fromF + video.durationF) * streamerScale + streamerFrame*streamerScale
            if e2 < 0:
                e2 = 0
            if e2 > 1000:
                e2 = 1000
            editor.canvas.create_rectangle(200 + e1, 600+n,
                                           200 + e2, 620+n, fill='#aaf')
            editor.canvas.create_text(
                700, 610 + n, text=video.path +
                ', from frame ' + str(video.start) +
                ', duration: ' + str(video.durationF) +
                ' frames, trimmed ' + str(video.fromF) +
                ' first frames', font=('Ariel', 7))
            editor.canvas.create_rectangle(160, 600+n, 200, 620+n, fill='#aaa')
            editor.canvas.create_text(
                180, 610+n, text='#'+str(p//20+1), font=('Ariel', 10))
        p += 20
        if n > 140:
            break
    del n, p

    # streamer sector and scale change buttons
    editor.canvas.create_text(180, 790, text='scale:%d%%' %
                              (streamerScale*100), font=('Ariel', 5))
    editor.canvas.create_rectangle(200, 780, 240, 800, fill='#aaa')
    editor.canvas.create_text(220, 790, text='segm:%d' %
                              (streamerPos+1), font=('Ariel', 5))
    editor.canvas.create_rectangle(240, 780, 280, 800, fill='#aaa')
    editor.canvas.create_polygon(260, 785, 255, 795, 265, 795, fill='green')
    editor.canvas.create_rectangle(280, 780, 320, 800, fill='#aaa')
    editor.canvas.create_polygon(300, 795, 295, 785, 305, 785, fill='green')
    editor.canvas.create_rectangle(320, 780, 360, 800, fill='#aaa')
    editor.canvas.create_polygon(334, 784, 336, 784, 340, 788, 344, 784,
                                 346, 784, 346, 786, 342, 790, 346, 794,
                                 346, 796, 344, 796, 340, 792, 336, 796,
                                 334, 796, 334, 794, 338, 790, 334, 786,
                                 fill='red')  # just cross form
    editor.canvas.create_rectangle(360, 780, 400, 800, fill='#aaa')
    editor.canvas.create_polygon(380, 785, 382, 787, 381, 787, 381, 789,
                                 282, 789, 383, 788, 385, 790, 383, 792,
                                 383, 791, 381, 791, 381, 793, 382, 793,
                                 380, 795, 378, 793, 379, 793, 379, 791,
                                 377, 791, 377, 792, 375, 790, 377, 788,
                                 377, 789, 379, 789, 379, 787, 378, 787,
                                 fill='blue')  # 3 downarrows
    editor.canvas.create_rectangle(400, 780, 440, 800, fill='#aaa')
    editor.canvas.create_oval(413, 783, 427, 797, fill='orange')
    editor.canvas.create_oval(415, 785, 425, 795, fill='#aaa')
    editor.canvas.create_polygon(422, 790, 430, 790, 426, 793, fill='orange')  # refresh
    editor.canvas.create_rectangle(440, 780, 480, 800, fill='#aaa')
    editor.canvas.create_text(460, 790, text='frame:%d' %
                              (streamerFrame+1), font=('Ariel', 5))
    editor.canvas.create_rectangle(480, 780, 520, 800, fill='#aaa')
    editor.canvas.create_polygon(490, 790, 510, 795, 510, 785, fill='green')
    editor.canvas.create_rectangle(520, 780, 560, 800, fill='#aaa')
    editor.canvas.create_polygon(550, 790, 530, 795, 530, 785, fill='green')

    # preview generator
    if oldPreviewFe != previewFrame or generatePreview:
        generatePreview = False
        if If.preview(previewFrame, effects):
            img = Image.open('/tmp/vira/prew.gif')
            img = img.resize((1000, 500), Image.ANTIALIAS)
            editor.tk.image = previewImage = ImageTk.PhotoImage(img)
            del img
            oldPreviewFe = previewFrame
        else:
            previewImage = None  # if none of videos there

    # effects
    effectN = 0
    visible_effects = []
    effect_in_list = -1
    effect_in_visibles = -1
    for effect in effects.applied_effects:
        effect_in_list += 1
        if effect.stream == selected_stream:
            effect_in_visibles += 1
            max_dur_effect = (1000-streamerFrame*streamerScale)/streamerScale-effect.start
            dur_effect = effect.duration if effect.duration != -1 else max_dur_effect
            if dur_effect > max_dur_effect:
                dur_effect = max_dur_effect
            if effect.start*streamerScale+streamerFrame*streamerScale > 0:
                startOfThisEffect = effect.start*streamerScale+streamerFrame*streamerScale
            else:
                startOfThisEffect = 0
            if startOfThisEffect > 1000:
                startOfThisEffect = 1000
            editor.canvas.create_rectangle(startOfThisEffect+200,
                                           600+effect_in_visibles*3,
                                           (dur_effect+effect.start)*
                                           streamerScale+streamerFrame*streamerScale+200,
                                           600+effect_in_visibles*3+1,
                                           fill='orange', outline='orange')
            visible_effects.append((120+effectN, effect_in_list))
            editor.canvas.create_rectangle(0, 120+effectN, 200,
                                           160+effectN+len(effect.vals)*20,
                                           fill='#aaa')
            editor.canvas.create_rectangle(0, 120+effectN,
                                           200, 160+effectN, fill='#fff')
            effect_strings = 40
            editor.canvas.create_text(100, 130+effectN,
                                      text=effect.__class__.__name__)
            editor.canvas.create_polygon(184, 134+effectN,
                                         186, 134+effectN,
                                         190, 138+effectN,
                                         194, 134+effectN,
                                         196, 134+effectN,
                                         196, 136+effectN,
                                         192, 140+effectN,
                                         196, 144+effectN,
                                         196, 146+effectN,
                                         194, 146+effectN,
                                         190, 142+effectN,
                                         186, 146+effectN,
                                         184, 146+effectN,
                                         184, 144+effectN,
                                         188, 140+effectN,
                                         184, 136+effectN, fill='red')
            editor.canvas.create_polygon(10, 130+effectN,
                                         20, 130+effectN,
                                         15, 120+effectN, fill='blue')
            editor.canvas.create_polygon(10, 150+effectN,
                                         20, 150+effectN,
                                         15, 160+effectN, fill='blue')
            editor.canvas.create_text(100, 140+effectN,
                                      text=effect.__doc__, font=('Ariel', 5))
            for value in effect.vals:
                editor.canvas.create_text(100, 130+effectN+effect_strings,
                                          text=value+': ' +
                                          str(effect.data[value]),
                                          font=('Ariel', 5))
                effect_strings += 20
                if effectN+effect_strings > 470:
                    del effects.applied_effects[effect_in_list]
                    editor.canvas.create_text(700, 400, text='too many effects',
                                              font=('Ariel', 100), fill='red')
                    refreshPreview()
            effectN += effect_strings

    # display preview
    if previewImage:
        editor.canvas.create_image((200, 100), anchor='nw', image=previewImage)
    else:
        editor.canvas.create_rectangle(200, 100, 1200, 600, fill='#aaa')
    current_mask_point = 0
    for xm,ym in mask_points:
        x = int(xm/If.clip_size_Y*1000+200)
        y = int(ym/If.clip_size_X*500+100)
        if round((editor.mouse[0]-200)*If.clip_size_Y/10000) == round(xm/10) and round((editor.mouse[1]-100)*If.clip_size_X/5000) == round(ym/10):
            editor.canvas.create_oval(x-5,y-5,x+5,y+5, outline='green', fill='blue')
        elif current_mask_point == selected_mask_point:
            editor.canvas.create_oval(x-5,y-5,x+5,y+5, outline='green', fill='red')
        else:
            editor.canvas.create_oval(x-5,y-5,x+5,y+5, outline='blue')
        current_mask_point += 1

    # preview position line
    if previewFrame*streamerScale+streamerFrame*streamerScale > 0 and previewFrame*streamerScale+streamerFrame*streamerScale < 1000:
        editor.canvas.create_line(previewFrame*streamerScale+streamerFrame*streamerScale+200, 600,
                                  previewFrame*streamerScale+streamerFrame*streamerScale+200, 780,
                                  fill='red')
        editor.canvas.create_text(previewFrame*streamerScale+streamerFrame*streamerScale+200, 590,
                                  text=str(int(previewFrame)), fill='red')
    if streamerFrame*streamerScale > 0 and streamerScale+streamerFrame*streamerScale < 1000:
        editor.canvas.create_line(streamerFrame*streamerScale+200, 600,
                                  streamerFrame*streamerScale+200, 780,
                                  fill='green')

    editor.update()  # update window data (menus etc.)
