#!/usr/env/python3
import ffmpeg_user, os, pickle, copy
from PIL import Image
import numpy as np
from pydub import AudioSegment
os.system('mkdir /tmp/vira')
clip_size_X, clip_size_Y = 1920, 1080


# --------------------Video in editor has extra data and is different
class Video:
    def __init__(self, path, start=0, fromF=0, durationF=0, transparent=0):
        self.transparency = transparent
        self.mask = None
        self.path = path
        self.start = start
        self.fromF = fromF
        # extract duration, long command
        f = open('/tmp/vira/name', 'w')
        f.write(path)
        f.close()
        os.system("ffprobe `cat /tmp/vira/name` -show_format 2>&1 | sed -n 's/duration=//p' > /tmp/vira/data")
        self.len = int(float(open('/tmp/vira/data').read())*24)
        if durationF > 0:
            self.durationF = durationF
        else:
            self.durationF = self.len


videos = []
Len = 1000
SAVABLE = True


def preview(l, effects):
    """generate preview to /tmp/vira/prew.gif"""
    succesful = False
    I = np.zeros((clip_size_X, clip_size_Y, 3))
    stream = len(videos)+1
    print(stream)
    videosFlipped = copy.copy(videos)
    videosFlipped.reverse()
    for v in videosFlipped:
        stream -= 1
        if v.start <= l and v.start+v.durationF >= l:
            path = videos.index(v)
            frame = l-videos[path].start+videos[path].fromF+1
            string = videos[path].path
            f = open('/tmp/vira/name', 'w')
            f.write(string)
            f.close()
            os.system(
                'ffmpeg -y -r 25 -ss %f -i `cat /tmp/vira/name` -vframes 1  /tmp/vira/prewiev.png' %
                (frame/25))
            for effect in effects.applied_effects:
                try:
                    print(stream)
                    effect.apply('/tmp/vira/prewiev.png', stream, l)
                except:
                    os.system('zenity --error --text="applying effect error"')
            effects.apply_imagemagick()
            print(np.asarray(Image.open('/tmp/vira/prewiev.png').convert('RGB')).shape)
            I2 = np.resize(np.asarray(Image.open('/tmp/vira/prewiev.png').convert('RGB')), (clip_size_X, clip_size_Y, 3))
            if v.mask is None:
                I = I*v.transparency+I2*(1-v.transparency)
            else:
                mask = np.resize(np.asarray(Image.open(v.mask).convert('RGB')), (clip_size_X, clip_size_Y, 3))
                I = I*mask/255+I2*(1-mask/255)
            succesful = True
    Image.fromarray(np.uint8(I)).save('/tmp/vira/prew.gif')
    return succesful


##def export(pathOut, effects):
##    """export video"""
##    pathlist = []
##    for l in range(Len):
##        for v in videos:
##            if v.start <= l and v.start+v.durationF >= l:
##                pathlist.append((l, videos.index(v)))
##                break
##    vids = []
##    for v in videos:
##        vids.append(ffmpeg_user.Video(v.path))
##    out = ffmpeg_user.Empty()
##    for f in range(len(pathlist)):
##        os.system('cp /tmp/vira/%s/frame%d.png /tmp/vira/%s/frame%d.png' %
##                  (vids[pathlist[f][1]].name,
##                   f - videos[pathlist[f][1]].start +
##                   videos[pathlist[f][1]].fromF+1,
##                   out.name, out.len))
##        stream = int(vids[pathlist[f][1]].name)-1
##        current_frame = out.len
##        out.len += 1
##        for effect in effects.applied_effects:
##            try:
##                effect.apply('/tmp/vira/%s/frame%d.png'%(out.name, current_frame),
##                             stream, current_frame)
##            except:
##                os.system('zenity --error --text="applying effect error!"')
##        effects.apply_imagemagick_slow()
##    out.export(str(pathOut) if str(pathOut) != '' else 'out.mp4')
def export(pathOut, effects, turbo=True, FPS=30):
    """export video"""
    out = ffmpeg_user.Empty()
    videosFlipped = copy.copy(videos)
    videosFlipped.reverse()
    vids = {}
    for v in videosFlipped:
        vids[v] = ffmpeg_user.Video(v.path, FPS=FPS)
    pathlist = 0
    for l in range(Len):
        for v in videos:
            if v.start <= l and v.start+v.durationF >= l:
                pathlist += 1
                break
    for frame in range(pathlist):
        I = np.zeros((clip_size_X, clip_size_Y, 3))
        stream = len(videos)+1
        for v in videosFlipped:
            stream -= 1
            if v.start <= frame and v.start+v.durationF >= frame:
                frameInside = frame-v.start+1
                for effect in effects.applied_effects:
                    try:
                        effect.apply('/tmp/vira/%s/frame%d.png'%(vids[v].name,frameInside),
                                     stream, frame)
                    except:
                        os.system('zenity --error --text="applying effect error!"')
    if turbo:
        effects.apply_imagemagick_slow()
    else:
        effects.apply_imagemagick()
    audios = []
    for frame in range(pathlist):
        I = np.zeros((clip_size_X, clip_size_Y, 3))
        stream = len(videos)+1
        last_video_ = None
        for v in videosFlipped:
            stream -= 1
            if v.start <= frame and v.start+v.durationF >= frame:
                frameInside = frame-v.start+1
                I2 = np.resize(np.asarray(Image.open('/tmp/vira/%s/frame%d.png'%(vids[v].name,frameInside)).convert('RGB')), (clip_size_X, clip_size_Y, 3))
                if v.mask is None:
                    I = I*v.transparency+I2*(1-v.transparency)
                else:
                    mask = np.resize(np.asarray(Image.open(v.mask).convert('RGB')), (clip_size_X, clip_size_Y, 3))
                    I = I*mask/255+I2*(1-mask/255)
                last_video_ = (vids[v].name, frameInside)
        Image.fromarray(np.uint8(I)).save('/tmp/vira/%s/frame%d.png'%(out.name, out.len))
        out.len += 1
        audios.append(last_video_)
    a = AudioSegment.empty()
    for u in audios:
        if u is None:
            a += AudioSegment.silent(duration=1000/FPS)
        else:
            if os.path.isfile('/tmp/vira/%s/audio.wav'%u[0]):
                i = AudioSegment.from_wav('/tmp/vira/%s/audio.wav'%u[0])[u[1]*1000/FPS:u[1]*1000/FPS+1000/FPS]
            else:
                i = AudioSegment.silent(duration=1000/FPS)
            a = a+i
    for v in vids:
        vids[v].rm()
    a.export('/tmp/vira/%s/audio.wav'%out.name, format='wav')
    out.export(str(pathOut) if str(pathOut) != '' else 'out.mp4', FPS=FPS)
    out.rm()


def pack(path='packed', effects=[]):
    """save data including videos used"""
    if path.endswith('.packedbyviravideo'):
        pass
    else:
        path += '.packedbyviravideo'
    out = []
    for video in videos:
        f = open('/tmp/vira/name', 'w')
        f.write(video.path)
        f.close()
        os.system('ffmpeg -y -r 25 -i `cat /tmp/vira/name` /tmp/vira/out.avi')
        out.append((video.start, video.fromF, video.durationF,
                    open('/tmp/vira/out.avi', 'rb').read(), video.transparency, open(video.mask, 'rb').read() if video.mask is not None else None))
    file = open(path, 'wb')
    pickle.dump([out, effects], file)
    file.close()


def save(path='saved', effects=[]):
    """save data excluding videos used"""
    if not SAVABLE:
        pack(path)
        return
    if path.endswith('.savedbyviravideo'):
        pass
    else:
        path += '.savedbyviravideo'
    out = []
    for video in videos:
        out.append((video.start, video.fromF, video.durationF, video.path, video.transparency, video.mask))
    file = open(path, 'wb')
    pickle.dump([out, effects], file)
    file.close()


def openF(path):
    """open data as unpack and openV relatively"""
    global videos, SAVABLE
    videos = []
    unpacked, effects = pickle.load(open(path, 'rb'))
    if len(unpacked) > 0:
        if isinstance(unpacked[0][3], bytes):
            os.system('mkdir /tmp/vira/unpacked')
            ID = 0
            for vid in unpacked:
                file = open('/tmp/vira/unpacked/%d.avi' % ID, 'wb')
                file.write(vid[3])
                file.close()
                videos.append(Video('/tmp/vira/unpacked/%d.avi' % ID,
                                    vid[0], vid[1], vid[2]))
                if len(vid) > 4:
                    videos[-1].transparency = vid[4]
                    if vid[5] is not None:
                        file = open('/tmp/vira/unpacked/mask%d.png' % ID, 'wb')
                        file.write(vid[5])
                        file.close()
                        videos[-1].mask = '/tmp/vira/unpacked/mask%d.png' % ID
                ID += 1
            SAVABLE = False
        else:
            for vid in unpacked:
                videos.append(Video(vid[3], vid[0], vid[1], vid[2]))
                if len(vid) > 4:
                    videos[-1].transparency = vid[4]
                    videos[-1].mask = vid[5]
            SAVABLE = True
    return effects


def new():
    """create new project"""
    global videos, SAVABLE
    videos = []
    SAVABLE = True
