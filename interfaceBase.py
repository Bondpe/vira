#!/usr/env/python3
import ffmpeg_user, os, pickle
os.system('mkdir /tmp/vira')
#-------------------------------------------------------------------------------------------------Video in editor has extra data and is different
class Video:
    def __init__(self, path, start=0, fromF=0, durationF=0):
        self.path = path
        self.start = start
        self.fromF = fromF
        os.system("ffprobe %s -show_format 2>&1 | sed -n 's/duration=//p' > /tmp/vira/data"%path)
        self.len = int(float(open('/tmp/vira/data').read())*24)
        if durationF > 0:
            self.durationF = durationF
        else:
            self.durationF = self.len
videos = []
Len = 1000

def preview(l):
    for v in videos:
        if v.start <= l and v.start+v.durationF >= l:
            path = videos.index(v)
            frame = l-videos[path].start+videos[path].fromF+1
            string = videos[path].path
            os.system('ffmpeg -y -r 25 -ss %f -i %s -vframes 1  /tmp/vira/prew.gif'%(frame/25, string))
            return True
    return False

def export(pathOut='out.mp4'):
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
        os.system('cp /tmp/vira/%s/frame%d.png /tmp/vira/%s/frame%d.png'%(vids[pathlist[f][1]].name, f-videos[pathlist[f][1]].start+videos[pathlist[f][1]].fromF+1, out.name, out.len))
        out.len += 1
    out.export(str(pathOut) if str(pathOut) != '' else 'out.mp4')
def pack(path='packed'):
    path += '.packedbyviravideo'
    out = []
    for video in videos:
        os.system('ffmpeg -y -r 25 -i %s /tmp/vira/out.avi'%(video.path))
        out.append((video.start, video.fromF, video.durationF, open('/tmp/vira/out.avi', 'rb').read()))
    file = open(path, 'wb')
    pickle.dump(out, file)
    file.close()
def save(path='saved'):
    path += '.savedbyviravideo'
    out = []
    for video in videos:
        out.append((video.start, video.fromF, video.durationF, video.path))
    file = open(path, 'wb')
    pickle.dump(out, file)
    file.close()
def unpack(path):
    global videos
    videos = []
    unpacked = pickle.load(open(path, 'rb'))
    os.system('mkdir /tmp/vira/unpacked')
    ID = 0
    for vid in unpacked:
        file = open('/tmp/vira/unpacked/%d.avi'%ID, 'wb')
        file.write(vid[3])
        file.close()
        videos.append(Video('/tmp/vira/unpacked/%d.avi'%ID, vid[0], vid[1], vid[2]))
        ID += 1
def openV(path):
    global videos
    videos = []
    unpacked = pickle.load(open(path, 'rb'))
    for vid in unpacked:
        videos.append(Video(vid[3], vid[0], vid[1], vid[2]))
def openF(path):
    global videos
    videos = []
    unpacked = pickle.load(open(path, 'rb'))
    if len(unpacked) > 0:
        if type(unpacked[0][3]) == type(b'a'):
            os.system('mkdir /tmp/vira/unpacked')
            ID = 0
            for vid in unpacked:
                file = open('/tmp/vira/unpacked/%d.avi'%ID, 'wb')
                file.write(vid[3])
                file.close()
                videos.append(Video('/tmp/vira/unpacked/%d.avi'%ID, vid[0], vid[1], vid[2]))
                ID += 1
        else:
            for vid in unpacked:
                videos.append(Video(vid[3], vid[0], vid[1], vid[2]))
