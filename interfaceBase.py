#!/usr/env/python3
import ffmpeg_user
import os
import pickle
os.system('mkdir /tmp/vira')


# --------------------Video in editor has extra data and is different
class Video:
    def __init__(self, path, start=0, fromF=0, durationF=0):
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
    stream = 0
    for v in videos:
        stream += 1
        if v.start <= l and v.start+v.durationF >= l:
            path = videos.index(v)
            frame = l-videos[path].start+videos[path].fromF+1
            string = videos[path].path
            f = open('/tmp/vira/name', 'w')
            f.write(string)
            f.close()
            os.system(
                'ffmpeg -y -r 25 -ss %f -i `cat /tmp/vira/name` -vframes 1  /tmp/vira/prew.gif' %
                (frame/25))
            for effect in effects.applied_effects:
                try:
                    effect.apply('/tmp/vira/prew.gif', stream, l)
                except:
                    os.system('zenity --error --text="applying effect error"')
            effects.apply_imagemagick()
            return True
    return False


def export(pathOut, effects):
    """export video"""
    pathlist = []
    for l in range(Len):
        for v in videos:
            if v.start <= l and v.start+v.durationF >= l:
                pathlist.append((l, videos.index(v)))
                break
    vids = []
    for v in videos:
        vids.append(ffmpeg_user.Video(v.path))
    out = ffmpeg_user.Empty()
    for f in range(len(pathlist)):
        os.system('cp /tmp/vira/%s/frame%d.png /tmp/vira/%s/frame%d.png' %
                  (vids[pathlist[f][1]].name,
                   f - videos[pathlist[f][1]].start +
                   videos[pathlist[f][1]].fromF+1,
                   out.name, out.len))
        stream = int(vids[pathlist[f][1]].name)-1
        current_frame = out.len
        out.len += 1
        for effect in effects.applied_effects:
            try:
                effect.apply('/tmp/vira/%s/frame%d.png'%(out.name, current_frame),
                             stream, current_frame)
            except:
                os.system('zenity --error --text="applying effect error!"')
        effects.apply_imagemagick_slow()
    out.export(str(pathOut) if str(pathOut) != '' else 'out.mp4')


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
                    open('/tmp/vira/out.avi', 'rb').read()))
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
        out.append((video.start, video.fromF, video.durationF, video.path))
    file = open(path, 'wb')
    pickle.dump([out, effects], file)
    file.close()


def unpack(path):
    """open data including videos used"""
    global videos, SAVABLE
    videos = []
    unpacked, effects = pickle.load(open(path, 'rb'))
    os.system('mkdir /tmp/vira/unpacked')
    ID = 0
    for vid in unpacked:
        file = open('/tmp/vira/unpacked/%d.avi' % ID, 'wb')
        file.write(vid[3])
        file.close()
        videos.append(Video('/tmp/vira/unpacked/%d.avi' % ID,
                            vid[0], vid[1], vid[2]))
        ID += 1
    SAVABLE = False
    return effects


def openV(path):
    """open data excluding videos used"""
    global videos, SAVABLE
    videos = []
    unpacked, effects = pickle.load(open(path, 'rb'))
    for vid in unpacked:
        videos.append(Video(vid[3], vid[0], vid[1], vid[2]))
    SAVABLE = True
    return effects


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
                ID += 1
            SAVABLE = False
        else:
            for vid in unpacked:
                videos.append(Video(vid[3], vid[0], vid[1], vid[2]))
            SAVABLE = True
    return effects


def new():
    """create new project"""
    global videos, SAVABLE
    videos = []
    SAVABLE = True
