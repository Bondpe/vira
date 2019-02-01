#!/usr/env/python3
import ffmpeg_user, os
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
if __name__ == '__main__':
    videos.append(Video('/home/pi/Videos/FLUID.avi', durationF=50))
    videos.append(Video('/home/pi/Videos/fluid.mp4', durationF=50, start=25))
    Len = 200
    export()
