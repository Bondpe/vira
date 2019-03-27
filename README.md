# vira
Video editor for raspberry pi.<br />
DEVELOPMENT IN PROGRESS! Any bugs will be fixed, sorry for them.<br />
Hopefuly, not only for raspberry pi.
# how to run
git clone https://GitHub.com/bondpe/vira.git<br />
cd vira<br />
python3 interface.py
# how to use:
run program<br />
white rectangle on bottom is called "streamer", basically it's list of streams where top one is playing over bottom<br />
use Shift+A or Edit>Add to create new stream from video file<br />
if your preview looks wierd, check resolution in File > Preferences, it has to match image size<br />
you can add a lot of streams, resort them with blue 3-arrows key on bottom, delete with red X, move with arrow keys, cut with Shift+arrow keys and Ctrl+arrow keys, move&cut with Stream menu<br />
Select stream by clicking, add effects with "add effect" menu, they should appear on pink field on the left<br />
to delete effect use red X, to move it onto another stream, use blue arrow buttons<br />
to change effect settings, click on "ValueName: value" text<br />
to change effect duration and position (default: 0-infinity), click on header of effect<br />
effects are also shown on streamer as orange lines, they are shown and sorted as in the effects area<br />
Note: if you add too much effects, last will be intantly removed<br />
Also, every effect is slowing down preview as well as exporting A LOT<br />
You can navigate streamer with green arrow buttons there, click on "segm: n" button to seek to stream, click on "scale:n%" for changing streamer scale<br />
To save your work, File>Save, File>Save As or Edit>Pack, Ctrl+S, Ctrl+Shift+S or Ctrl+P<br />
Saving equals just linking video files to saved video, but file is smaller and opened file can be saved later<br />
Packing copies input files into packed file, you literally can't save unpacked file<br />
Also packing is slower, but much more stable<br />
opening packed&saved files works the same way: using File>Open<br />
to export your work, to save it as video file, use Edit>Export<br />
add masks, change video transparency (mask is a hole in a video)<br />
# create own effect
file has to look like this for now:
```
#viraeffect:0.0.1
comment (only shown in file)\name\inline-documentation\
var float:valueName,string:valueNameAnother
|all|
valuea=valueName**FRAME
value=valuea*2
#comment
# Pixels - just r, g and b values in 3-dimensional array
PIXELS/=value
[valueName>Frame]
#condition/\, \/ execute if true
    PIXELS*=valueName
#outside if-then
>FRAME
>value
#/\ - output
    PIXELS**=FRAME
#   still for that same condition
|/all|
```
another example, analise pixel by pixel
```
#viraeffect:0.0.2
\darken(keyframed)\RGB test effect (loaded)\
var float:darkness
|RGB|
d=X%3
[d=0]
    R=R/darkness
    G=0*0
    B=0*0
[d=1]
    B=B/darkness
    G=0*0
    R=0*0
[d=2]
    G=G/darkness
    R=0*0
    B=0*0
|/RGB|
```
5 additional input vars here: `R`, `G`, `B`, `X`, `Y`<br />
supported operations: `+`, `-`, `*`, `/`,`**`=`^`, `%`;
supported condition operations: `>`,`<`,`=`,`>=`,`<=`;
supported `PIXELS` operations: `*=`,`/=`,`**=`;
exactly 2 vars in one expression like `var=var1+var2`;
only one var in `>var`;
exactly 2 vars in `[var1=var2]`;
you may always use float as var in expression/`PIXELS*=`/`[a=b]`/`>var`;
you can't use `>PIXELS`;
