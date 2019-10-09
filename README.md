# vira
Video editor for raspberry pi.<br />
DEVELOPMENT IN PROGRESS! If you discover a bug, please report it on issues tab.<br />
Hopefuly, not only for raspberry pi.
# how to run
```
git clone https://GitHub.com/bondpe/vira.git
python3 vira/__main__.py
```
# how to use:
This is a completely renewed version of vira. The older version was completely different - slower, undevelopable etc.
<br /><br />
When you start a script, you see somewhat confusing window. To begin creating a project, you can click an 'Add' button, select a category and a datatype (for example, 'File>tmp-access video from file' which will load a video), and fill in all the popup inputs. Then you can start adding overlays ('Combine>colorkey stream'), reordering them (second button on right will move a datapack 1 stream up). If you want to delete the stream, click on the red cross on the right.
<br /><br />
To navigate streams area, use your middle mouse button for dragging, and drag with right mouse button to zoom in/out. When you left-click, you select the stream and move the time cursor to that position.
<br /><br />
If you want to edit any streams input data, then right-click on blue rectangle on upper right, then left-click on input you'd want to change. You can also enter new streams name there , by clicking 'save new name' after done.
<br /><br />
If you have some overlay datapacks, their names will appear in white squares on upper right. To delete an overlay, simply left-click on it. To edit its data, right-click - the same dialog will appear.
<br /><br />
You can use 'Basic>Combine several clips' datapack. In the dialog window select all streams that you'd like to put into a single object, then close the window. You'll see that all of your selected streams turned into a single object. If you'd like to edit them, right-click the blue rectangle while having composed stream selected, and click on 'streams multi-stream sequence'. Then you'll enter the composition. To return, simply click on 'Go to root composition' button. You can have as many overlayed compositions as you want to.
<br /><br />
To export the clip, use upper 'Export button', and fill in all the required forms. There also is a thing called 'Prewiev exporting' - the button near the 'Play/pause' button exports only the composition you're in, without exporting the sound. During export process the editor may freeze.
# not using linux?
Change some values in 'constants.py' file!
