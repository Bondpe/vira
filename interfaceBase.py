#!/usr/env/python3
import ffmpeg_user, os
#-------------------------------------------------------------------------------------------------Video in editor has extra data and is different
class Video:
    def __init__(self, path, start=0, fromF=0, durationF=100):
        self.path = path
        self.start = start
        self.fromF = fromF
        self.durationF = durationF
videos = []
Len = 1000

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
if __name__ == '__main__':
    videos.append(Video('/home/pi/Videos/FLUID.avi', durationF=50))
    videos.append(Video('/home/pi/Videos/fluid.mp4', durationF=50, start=25))
    Len = 200
    export()
