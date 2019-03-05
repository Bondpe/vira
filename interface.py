#!/usr/env/python3
import sys
import interfaceBase as If
import effects
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk
# ---------------------------------Create window
from window import Window
editor = Window(1400, 800, '#000')
editor.tk.title('vira v0.0.2')
# ---------------------------------Initialise functions
# ============================ File
projectPath = None


def newVideo():
    global projectPath
    If.new()
    effects.applied_effects = []
    projectPath = None
    editor.tk.title('vira v0.0.2')


def openVideo():
    global projectPath
    path = filedialog.Open(editor.tk).show()
    if path == () or path == '':
        return
    effects.applied_effects = If.openF(path)
    projectPath = path
    editor.tk.title('vira v0.0.2 - '+path)


def saveAsVideo():
    global projectPath
    path = filedialog.SaveAs(editor.tk).show()
    If.save(path, effects.applied_effects)
    projectPath = path
    editor.tk.title('vira v0.0.2 - '+path)


def saveVideo():
    global projectPath
    if projectPath is None:
        saveAsVideo()
    else:
        If.save(projectPath, effects.applied_effects)


def exq():
    editor.tk.destroy()
    sys.exit()


# ============================ Edit


def Add():
    path = filedialog.Open(editor.tk).show()
    if path == () or path == '':
        return
    If.videos.append(If.Video(path))
    return


def export():
    path = filedialog.SaveAs(editor.tk).show()
    If.export(path, effects.applied_effects)


def pack():
    path = filedialog.SaveAs(editor.tk).show()
    If.pack(path, effects.applied_effects)


editor.create_down_menu(30, 0, 60, 15, 'Edit', [
                        'Add', 'Export', 'Pack'], [Add, export, pack])
# ============================ Stream
selected_stream=1
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


def change_from():
    global selected_stream, streamerPos
    stream = selected_stream+streamerPos-1
    if len(If.videos) <= stream:
        return
    start = simpledialog.askinteger(
        "Change stream data (start)", "stream start at self-frame\n(%s):" %
        If.videos[stream].path, initialvalue=0) - 1
    If.videos[stream].fromF = start


def change_len():
    global selected_stream, streamerPos
    stream = selected_stream+streamerPos-1
    if len(If.videos) <= stream:
        return
    start = simpledialog.askinteger(
        "Change stream data (start)", "streams last frame\n(%s):" %
        If.videos[stream].path, initialvalue=0)-1
    If.videos[stream].durationF = start+If.videos[stream].start


editor.create_down_menu(60, 0, 110, 15, 'Stream', [
                        'Change start', 'Cut start', 'Cut duration'],
                        [change_start,   change_from, change_len])
# ~~preview
previewImage = None
previewFrame = 0
oldPreviewFe = 0
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


for n in range(9):
    exec('''def set_selected():
    global selected_stream, streamerPos
    selected_stream = %d+streamerPos
editor.create_clicker(150, 600+n*20, 1200, 620+n*20, set_selected)'''%(n+1))


#-------effects
editor.create_rectangle(0, 100, 200, 600, fill='#baa')

effectFuncs = []
for name in effects.names:
    exec('''
global effectFuncs
def fun():
    effects.apply(%s)
    for val in effects.applied_effects[-1].vals:
        effects.applied_effects[-1].data[val] = simpledialog.askfloat(
        "Add image effect", val, initialvalue=1)
    effects.applied_effects[-1].stream = selected_stream
effectFuncs.append(fun)'''%('"'+name+'"'))

editor.create_down_menu(0, 100, 200, 115, 'add', effects.names, effectFuncs)


#------end

editor.create_down_menu(0, 0, 30, 15, 'File',
                        ['New',   'Open',    'Save',    'Save as',   'Quit'],
                        [newVideo, openVideo, saveVideo, saveAsVideo, exq])

while True:
    # streamer area fill
    editor.canvas.create_rectangle(200, 600, 1200, 800, fill='#eee')
    editor.canvas.create_rectangle(160, 600, 200, 800, fill='#aaa')

    # display streams
    p, n = 0, 0
    editor.canvas.create_rectangle(
            150, 580+selected_stream*20-streamerPos*20, 1200, 600+selected_stream*20-streamerPos*20, fill='#00d')
    for video in If.videos:
        n = p-streamerPos*20
        if n >= 0:
            editor.canvas.create_rectangle(
                200, 600+n, 1200, 620+n, fill='#ddd')
            editor.canvas.create_rectangle(200 + (video.start - video.fromF) *
                                           streamerScale, 600+n,
                                           200 + (video.start - video.fromF +
                                                  video.len) *
                                           streamerScale, 620+n, fill='#ffa')
            editor.canvas.create_rectangle(200 + (video.start) *
                                           streamerScale, 600+n,
                                           200 + (video.start - video.fromF +
                                                  video.durationF) *
                                           streamerScale, 620+n, fill='#aaf')
            editor.canvas.create_text(
                700, 610+n, text=video.path, font=('Ariel', 5))
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

    # preview generator
    if oldPreviewFe != previewFrame:
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

    # effects
    effectN = 0
    for effect in effects.applied_effects:
        if effect.stream == selected_stream:
            editor.canvas.create_text(100, 130+effectN, text=effect.__class__.__name__)
            effectN += 20

    editor.update()  # update window data (menus etc.)
