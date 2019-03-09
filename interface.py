#!/usr/env/python3
import sys, effects
import interfaceBase as If
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk
# ---------------------------------Create window
from window import Window
editor = Window(1400, 800, '#000')
version='0.0.8'
editor.tk.title('vira v'+version)
generatePreview = False
# ---------------------------------Initialise functions
import loadEffect
loadEffect.main(effects, editor, filedialog)

def refreshPreview():
        global generatePreview
        generatePreview = True


editor.create_clicker(400, 780, 440, 800, refreshPreview)


# ============================ File
projectPath = None


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
    effects.applied_effects = If.openF(path)
    projectPath = path
    editor.tk.title('vira v'+version+' - '+path)
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
    If.export(path, effects.applied_effects)


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


# ~~preview
previewImage = None
previewFrame = 1
oldPreviewFe = 1
streamerScale = 1


def newPreview():
    global previewFrame, streamerScale
    previewFrame = (editor.mouse[0]-200)/streamerScale


editor.create_clicker(200, 600, 1200, 780, newPreview)
# ~~streams
# scale


def newScale():
    global streamerScale
    streamerScale = simpledialog.askinteger("Streamer", "New scale (%)")/100


editor.create_clicker(160, 780, 200, 800, newScale)
# pos


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
            if value_type == 'str':
                effects.applied_effects[n].data[value] = simpledialog.askstring(
                    "Edit image effect", value,
                    initialvalue=effects.applied_effects[n].data[value])
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

editor.create_down_menu(0, 0, 30, 15, 'File',
                        ['New',   'Open',    'Save',    'Save as',   'Quit'],
                        [newVideo, openVideo, saveVideo, saveAsVideo, exq])
editor.create_down_menu(30, 0, 60, 15, 'Edit', [
                        'Add', 'Export', 'Pack'], [Add, export, pack])
editor.create_down_menu(60, 0, 110, 15, 'Stream', [
                        'Change start', 'Cut start', 'Cut duration'],
                        [change_start,   change_from, change_len])



while True:
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
            e1 = (video.start - video.fromF) * streamerScale
            if e1 < 0:
                e1 = 0
            if e1 > 1000:
                e1 = 1000
            e2 = (video.start - video.fromF + video.len) * streamerScale
            if e2 < 0:
                e2 = 0
            if e2 > 1000:
                e2 = 1000
            editor.canvas.create_rectangle(200 + e1, 600+n,
                                           200 + e2, 620+n, fill='#ffa')
            e1 = video.start * streamerScale
            if e1 < 0:
                e1 = 0
            if e1 > 1000:
                e1 = 1000
            e2 = (video.start - video.fromF + video.durationF) * streamerScale
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

    # preview generator
    if oldPreviewFe != previewFrame or generatePreview:
        generatePreview = False
        if If.preview(previewFrame, effects.applied_effects):
            img = Image.open('/tmp/vira/prew.gif')
            img = img.resize((1000, 500), Image.ANTIALIAS)
            editor.tk.image = previewImage = ImageTk.PhotoImage(img)
            del img
            oldPreviewFe = previewFrame
        else:
            previewImage = None  # if none of videos there

    # display preview
    if previewImage:
        editor.canvas.create_image((200, 100), anchor='nw', image=previewImage)
    else:
        editor.canvas.create_rectangle(200, 100, 1200, 600, fill='#aaa')

    # preview position
    editor.canvas.create_line(previewFrame*streamerScale+200, 600,
                              previewFrame*streamerScale+200, 780,
                              fill='red')
    editor.canvas.create_text(previewFrame*streamerScale+200, 590,
                              text=str(int(previewFrame)), fill='red')

    # effects
    effectN = 0
    visible_effects = []
    effect_in_list = -1
    effect_in_visibles = -1
    for effect in effects.applied_effects:
        effect_in_list += 1
        if effect.stream == selected_stream:
            effect_in_visibles += 1
            max_dur_effect = 1000/streamerScale-effect.start
            dur_effect = effect.duration if effect.duration != -1 else max_dur_effect
            if dur_effect > max_dur_effect:
                dur_effect = max_dur_effect
            editor.canvas.create_rectangle(effect.start*streamerScale+200,
                                           600+effect_in_visibles*3,
                                           (dur_effect+effect.start)*
                                           streamerScale+200,
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

    editor.update()  # update window data (menus etc.)
