# vira
Video editor for raspberry pi.<br />
DEVELOPMENT IN PROGRESS! If you discover a bug, please report it on issues tab.<br />
Hopefuly, not only for raspberry pi.<br />
Non-frame-based.
# how to run
```
git clone https://GitHub.com/bondpe/vira.git
python3 vira/__main__.py
```
# not using linux?
Try changing some values in 'constants.py' file!
# something doesn't work?
Make sure if that's not related to dependencies. You can also try disabling addons in 'constants.py' file. Also, if you think that's a bug, please report it on the issues tab.
# how to use:
This is a completely renewed version of vira. The older version was completely different (slower, undevelopable, only visual fx support etc.)
<br /><br />
The new window is seperated in four parts. The bottom area contains streams list (the bottom stream displays over others). The area on top contains the preview. The left area is the current stream editor. The area on right is for adding streams.
<br /><br />
To add the new stream, click the 'Add' button and select it, or select it from the area on the right; then fill in all the inputs.
<br />
To edit the current streams or any of its children/parents inputs, use the menu on the left. The 'e' button will open an editor that'll allow you to adit any input or to change the current streams/parents name. The 'X' will allow you todelete the parent, but never the furthest child in the stack.
<br />
To reorder streams use the buttor under the big redd cross on the right of the streams area. To delete the stream, use that red cross. To export the whole file, use the 'Export' button in the menu. The button under the preview, near the play button, will allow you to export the currently open composition image-only. To create the included composition use the 'Basic>Combine several clips', and click on the 'Multi stream sequence' input to open it. Use 'Go to root composition' button to exit it.
