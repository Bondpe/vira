import interface

try:
    e = interface.Editor()
    while True:
        e.update()
except:
    input()
