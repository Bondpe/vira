import random, os, logging, shutil, sys

_ = os.sep

temporary = '/tmp'
name = 'vira'+_
icon_path = os.path.dirname(os.path.abspath(__file__))+_+'icons'+_

try:
    os.mkdir(temporary+_+name)
except:
    shutil.rmtree(temporary+_+name)
    logging.info('temporary directory exists')
    os.mkdir(temporary+_+name)
temp_path = temporary+_+name

try:
    os.mkdir(name)
except:
    logging.info('temporary directory exists')
const_path = name

used_pathes = 0
def get_temp_path():
    global used_pathes
    used_pathes += 1
    return temp_path+str(used_pathes)

def get_plugin_list():
    return ['imagemagick', 'imageeffects', 'colorgrade'] # imagemagick broke

theme = {'bg':'#111','hbg':'#555', 'fbg':'#000', 'selected':'#033', 'non-selected':'#330', 'fg':'#fff', 'sfg':'#aaa', 'mark':'red'}
