import input, datamanagement, constants
import ffmpeg, copy, os, scipy
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def matchImageSize(a, b):
    s1 = a.shape
    s2 = b.shape
    s3 = []
    s3.append(max([s1[0], s2[0]]))
    s3.append(max([s1[1], s2[1]]))
    ia = Image.fromarray(np.uint8(a))
    ib = Image.fromarray(np.uint8(b))
    sa = ia.resize(s3)
    sb = ib.resize(s3)
    a = np.asarray(sa)
    b = np.asarray(sb)
    return (a,b)

class Basic:
    Tname = 'basic wrapper'
    argnames = {'child':None}
    argtype = {'child':'c'}
    category = 'Basic'
    argorder = None
    saveDefault = True
    def __init__(self, name=None):
        if name is None:
            name = self.Tname
        self.name = name
        self.args = copy.copy(self.argnames)
        if self.argorder is None:
            self.argkeys = sorted(list(self.args.keys()))
        else:
            self.argkeys = self.argorder
    def get(self, time, input):
        return self.args['child'].get(time, input)
    def sound(self, time, inval):
        return inval
    def setup(self):
        """this function is launched just after input data is completed"""
        pass
    def getStartEnd(self):
        """change this to return None or (StartTime, EndTime), for non-endless streams"""
        if 'child' in self.args:
            return self.args['child'].getStartEnd()
        return None
    def get_name(self):
        if 'child' in self.argtype and self.argtype['child'] == 'c':
            return self.args['child'].get_name()
        else:
            return self.name
    def is_box(self):
        return 'child' in self.argtype and self.argtype['child'] == 'c'
    def save(self, packer):
        return None
    def load(self, loader):
        return None

class Composition(Basic):
    Tname = 'Combine several clips'
    argnames = {'streams':None}
    argtype = {'streams':input.MultiStream}
    category = 'Basic'
    saveDefault = False
    def get(self, time, d):
        i = 0
        while len(self.args['streams'].streams) > i:
            d = self.args['streams'].streams[i][0].get(time-self.args['streams'].streams[i][1], d)
            i += 1
        return d
    def sound(self, time, d):
        i = 0
        while len(self.args['streams'].streams) > i:
            d = self.args['streams'].streams[i][0].sound(time-self.args['streams'].streams[i][1], d)
            i += 1
        return d
    def save(self, packer):
        streams = []
        for stream, delta in self.args['streams'].streams:
            streams.append([packer(stream),delta])
        return streams
    def load(self, data, loader):
        streams = []
        for packed, delta in data:
            streams.append([loader(*packed), delta])
        self.args['streams'] = self.argtype['streams'](streams)

class Black(Basic):
    Tname = 'black background'
    argnames = {'resolution':None}
    argtype = {'resolution':input.Resolution}
    category = 'Basic'
    def get(self, time, input):
        return np.zeros((self.args['resolution'].y, self.args['resolution'].x, 3))

class ColorMatte(Basic):
    category = 'Basic'
    Tname = 'filled background'
    argnames = {'resolution':None, 'color':None}
    argtype = {'resolution':input.Resolution, 'color':input.Color}
    def get(self, time, input):
        return np.array([self.args['color'].color]).repeat(self.args['resolution'].x*self.args['resolution'].y, 0).reshape((self.args['resolution'].y,self.args['resolution'].x,3))

class CropMove(Basic):
    Tname = 'crop/move sth.'
    argnames = {'child':None,'crop':None,'delta':None}
    argtype = {'child':'c','crop':input.TimeSegment,'delta':input.Time}
    category = 'Timing'
    def get(self, time, input):
        if time >= self.args['crop'].start and time <= self.args['crop'].end:
            return self.args['child'].get(time+self.args['delta'].time, input)
        return input
    def getStartEnd(self):
        start, end = self.args['crop'].time
        time = self.args['child'].getStartEnd()
        if time is not None:
            if start < time[0]:
                start = time[0]
            if end > time[1]:
                end = time[1]
        return (start, end)

class Alpha(Basic):
    category = 'Combine'
    Tname = 'add alpha to video'
    argnames = {'child':None,'alpha':None,'mode':None}
    argtype = {'child':'c','alpha':input.AlphaPercent,'mode':input.MixModes}
    def get(self, time, b):
        a = self.args['child'].get(time, b)
        if a is None:
            return b
        if a is not None and b is not None:
            a,b=matchImageSize(a,b)
            return self.args['mode'].run(a,b,self.args['alpha'].alpha)
        return a

class Layer(Basic):
    category = 'Combine'
    Tname = 'layer a channel'
    argnames = {'child':None,'mode':None}
    argtype = {'child':'c','mode':input.LayerModes}
    def get(self, time, b):
        a = self.args['child'].get(time, b)
        if a is None:
            return b
        if a is not None and b is not None:
            a,b=matchImageSize(a,b)
            return self.args['mode'].run(b,a)
        return a
    def getStartEnd(self):
        return self.args['child'].getStartEnd()


class ColorKey(Basic):
    category = 'Combine'
    Tname = 'colorkey stream'
    argnames = {'child':None,'Color':None, 'treshold':None}
    argtype = {'child':'c','Color':input.Color, 'treshold':input.Integer}
    def get(self, time, bg):
        a = self.args['child'].get(time, bg)
        if a is None:
            return bg
        if a is not None and bg is not None:
            a,bg = matchImageSize(a,bg)
            r,g,b = a[:,:,0], a[:,:,1], a[:,:,2]
            R = np.int_(abs(r-self.args['Color'].color[0])>(256-self.args['treshold'].num))
            G = np.int_(abs(g-self.args['Color'].color[1])>(256-self.args['treshold'].num))
            B = np.int_(abs(b-self.args['Color'].color[2])>(256-self.args['treshold'].num))
            key = (R+G+B)==3
##            key = a-np.array(self.args['Color'].color)>self.args['treshold'].num
##            key = np.int_(key)
##            key = (key[:,:,0]+key[:,:,1]+key[:,:,2])==np.amax(key[:,:,0]+key[:,:,1]+key[:,:,2])
            key = key.repeat(3,1).reshape(*key.shape+(3,))
            fgL = a*key
            bgL = bg*(1-key)
            return bgL+fgL
        return a
    def getStartEnd(self):
        return self.args['child'].getStartEnd()
    def setup(self):
        if self.args['Color'].color[0] == 0:
            self.args['Color'].color[0] = 1
            self.args['Color'].r = 1
        if self.args['Color'].color[1] == 0:
            self.args['Color'].color[1] = 1
            self.args['Color'].g = 1
        if self.args['Color'].color[2] == 0:
            self.args['Color'].color[2] = 1
            self.args['Color'].b = 1

class LinearFadeIn(Basic):
    category = 'Timing'
    Tname = 'linear fade-in'
    argnames = {'child':None,'time':None}
    argtype = {'child':'c','time':input.TimeSegment}
    def get(self, time, b):
        a = self.args['child'].get(time, b)
        if self.args['time'].start > time:
            return b
        if self.args['time'].end < time:
            return a
        if a is None:
            return b
        if a is not None and b is not None:
            a,b=matchImageSize(a,b)
            delta = time-self.args['time'].start
            segment = self.args['time'].end-self.args['time'].start
            t = delta/segment
            return a*t+b*(1-t)
        return a
    def getStartEnd(self):
        time = self.args['child'].getStartEnd()
        if time is None:
            return None
        start, end = time
        if self.args['time'].end > start:
            start = self.args['time'].start
        return (start, end)

class LinearFadeOut(Basic):
    category = 'Timing'
    Tname = 'linear fade-out'
    argnames = {'child':None,'time':None}
    argtype = {'child':'c','time':input.TimeSegment}
    def get(self, time, b):
        a = self.args['child'].get(time, b)
        if self.args['time'].start > time:
            return a
        if self.args['time'].end < time:
            return b
        if a is None:
            return b
        if a is not None and b is not None:
            a,b=matchImageSize(a,b)
            delta = time-self.args['time'].start
            segment = self.args['time'].end-self.args['time'].start
            t = 1-delta/segment
            return a*t+b*(1-t)
        return a
    def getStartEnd(self):
        time = self.args['child'].getStartEnd()
        if time is None:
            return None
        start, end = time
        if self.args['time'].start < end:
            end = self.args['time'].end
        return (start, end)


class QuickVideo(Basic):
    category = 'File'
    Tname = 'quick and memory-consuming video from file'
    argnames = {'file':None}
    argtype = {'file':datamanagement.Name}
    def get(self, time, input):
        frame = int(time*self.fps)
        if frame >= self.frames:
            return None
        return self.video[frame]
    def getStartEnd(self):
        return (0, self.frames/self.fps)
    def setup(self):
        probe = ffmpeg.probe(self.args['file'].data().path)
        video_info = next(x for x in probe['streams'] if x['codec_type'] == 'video')
        width = int(video_info['width'])
        height = int(video_info['height'])
        self.frames = int(video_info['nb_frames'])
        self.fps = int(video_info['r_frame_rate'].split('/')[0])/int(video_info['r_frame_rate'].split('/')[1])
        out, err = (ffmpeg
                    .input(self.args['file'].data().path)
                    .output('pipe:', format='rawvideo', pix_fmt='rgb24')
                    .run(capture_stdout=True)
        )
        self.video = np.frombuffer(out, np.uint8).reshape([-1, height, width, 3])


class Video(Basic):
    category = 'File'
    Tname = 'video from file'
    argnames = {'file':None}
    argtype = {'file':datamanagement.Name}
    def get(self, time, input):
        frame = int(time*self.fps)
        if frame >= self.frames:
            return None
        framenum = int(time*self.fps)
        if framenum in self.cache:
            return self.cache[framenum]
        out, err = (
            ffmpeg
            .input(self.args['file'].data().path)
            .filter('select', 'gte(n,{})'.format(framenum))
            .output('pipe:', vframes=1, format='rawvideo', pix_fmt='rgb24')
            .run(capture_stdout=True)
            )
        frame = np.frombuffer(out, np.uint8).reshape([self.height, self.width, 3])
        self.cache[framenum] = frame
        self.cacheold.append(framenum)
        if len(self.cacheold) > self.MAXLEN:
            del self.cache[self.cacheold[0]]
            del self.cacheold[0]
        return frame
    def getStartEnd(self):
        return (0, self.frames/self.fps)
    def setup(self):
        probe = ffmpeg.probe(self.args['file'].data().path)
        video_info = next(x for x in probe['streams'] if x['codec_type'] == 'video')
        self.width = int(video_info['width'])
        self.height = int(video_info['height'])
        self.frames = int(video_info['nb_frames'])
        self.fps = int(video_info['r_frame_rate'].split('/')[0])/int(video_info['r_frame_rate'].split('/')[1])
        self.cache = {}
        self.cacheold = []
        self.MAXLEN = 10


class TVideo(Basic):
    category = 'File'
    Tname = 'tmp-access video from file'
    argnames = {'file':None}
    argtype = {'file':datamanagement.Name}
    def get(self, time, input):
        frame = int(time*self.fps)
        if frame >= self.frames:
            return None
        framenum = int(time*self.fps)
        if framenum in self.cache:
            return self.cache[framenum]
        frame = np.asarray(Image.open(self.tmp+'/frame%s.jpg'%str(framenum).zfill(4))).reshape([self.height, self.width, 3])
        self.cache[framenum] = frame
        self.cacheold.append(framenum)
        if len(self.cacheold) > self.MAXLEN:
            del self.cache[self.cacheold[0]]
            del self.cacheold[0]
        return frame
    def sound(self, time, inval):
        rate, data = scipy.io.wavfile.read(self.tmp+'/audio.wav')
        val = data[int(time*rate)]
        print(val)
        return val
    def getStartEnd(self):
        return (0, self.frames/self.fps)
    def setup(self):
        probe = ffmpeg.probe(self.args['file'].data().path)
        video_info = next(x for x in probe['streams'] if x['codec_type'] == 'video')
        self.width = int(video_info['width'])
        self.height = int(video_info['height'])
        self.frames = int(video_info['nb_frames'])
        self.fps = int(video_info['r_frame_rate'].split('/')[0])/int(video_info['r_frame_rate'].split('/')[1])
        self.cache = {}
        self.cacheold = []
        self.MAXLEN = 10
        self.tmp = constants.get_temp_path()
        os.mkdir(self.tmp)
        out, err = (
            ffmpeg
            .input(self.args['file'].data().path)
            .output(self.tmp+'/audio.wav')
            .run()
        )
        out, err = (
            ffmpeg
            .input(self.args['file'].data().path)
            .output(self.tmp+'/frame%04d.jpg')
            .run()
        )


class Img(Basic):
    category = 'File'
    Tname = 'image from file'
    argnames = {'file':None}
    argtype = {'file':datamanagement.Name}
    def get(self, time, input):
        return self.frame
    def setup(self):
        self.frame = np.asarray(Image.open(self.args['file'].data().path).convert('RGB'))


class Mask(Basic):
    category = 'Combine'
    Tname = 'transparency mask'
    argnames = {'points':None, 'blur':None, 'child':None}
    argtype = {'points':input.PointArray, 'blur':input.Integer, 'child':'c'}
    def get(self, time, b):
        a = self.args['child'].get(time, b)
        if a is None:
            return b
        if a is not None and b is not None:
            a,b=matchImageSize(a,b)
            size = (a.shape[1], a.shape[0])
            if size in self.masks:
                mask = self.masks[size]
            else:
                im = Image.new("RGB", size)
                draw = ImageDraw.Draw(im)
                draw.polygon(self.args['points'].pos,fill=(255,255,255))
                im = im.filter(ImageFilter.GaussianBlur(radius=self.args['blur'].num)).resize(size)
                mask = np.asarray(im)
                self.masks[size] = mask
            return a*(mask/255)+b*(1-mask/255)
        return a
    def setup(self):
        self.masks = {}


class Paste(Basic):
    category = 'Combine'
    Tname = 'paste, not blend'
    argnames = {'pos':None, 'resolution':None, 'child':None}
    argtype = {'pos':input.Point, 'resolution':input.Resolution, 'child':'c'}
    def get(self, time, b):
        a = self.args['child'].get(time, b)
        if a is None:
            return b
        if a is not None and b is not None:
            ia = Image.fromarray(np.uint8(a))
            ib = Image.fromarray(np.uint8(b))
            ib.paste(ia.resize(self.args['resolution'].r), self.args['pos'].pos)
            return np.asarray(ib)
        return a


class Crop(Basic):
    category = 'Image manipulation'
    Tname = 'crop'
    argnames = {'pos1':None, 'pos2':None, 'child':None}
    argtype = {'pos1':input.Point, 'pos2':input.Point, 'child':'c'}
    def get(self, time, b):
        a = self.args['child'].get(time, b)
        return a[self.args['pos1'].x:self.args['pos2'].x][self.args['pos1'].y:self.args['pos2'].y]


class GhostPaste(Basic):
    category = 'Combine'
    Tname = 'paste and blend'
    argnames = {'pos':None, 'resolution':None, 'child':None, 'mode':None}
    argtype = {'pos':input.Point, 'resolution':input.Resolution, 'child':'c', 'mode':input.LayerModes}
    argorder = ['child', 'mode', 'resolution', 'pos']
    def get(self, time, b):
        a = self.args['child'].get(time, b)
        if a is None:
            return b
        if a is not None and b is not None:
            ia = Image.fromarray(np.uint8(a))
            if self.args['mode'].name in ['add', 'substract', 'screen', 'difference', 'darken only']:
                ib = Image.new('RGB', (b.shape[1], b.shape[0]), (0,0,0))
            else:
                ib = Image.new('RGB', (b.shape[1], b.shape[0]), (255,255,255))
            ib.paste(ia.resize(self.args['resolution'].r), self.args['pos'].pos)
            a = np.asarray(ib)
            return self.args['mode'].run(b,a)
        return a


avaliable = [Black, ColorMatte, CropMove, Video, QuickVideo, Img, Alpha, LinearFadeIn, LinearFadeOut, TVideo, Mask, Paste, Layer, GhostPaste, ColorKey, Composition]
