#!/usr/bin/env python3

#from luke_stim_types import *

from math import pi, sqrt
from time import sleep
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.dlpc350 import make_dlpc350_objects

def main():
    # Put lightcrafter(s) in pattern mode
    dlpc350_objects = make_dlpc350_objects()
    for dlpc350_object in dlpc350_objects:
         dlpc350_object.pattern_mode(fps=115.06)

    if len(dlpc350_objects) == 0:
        print('No lightcrafters detected! Try sudo') 

    w = 14.2e-2
    h = 9e-2
    d = (w/2) * sqrt(2)
    s = (w/2) / sqrt(2)

    right_screen = Screen(width=w, height=h, rotation=+pi/4, offset=(+s, -d + s, -h / 2), id=1, fullscreen=True, vsync=None, square_side=5e-2, square_loc='lr')
    left_screen = Screen(width=w, height=h, rotation=-pi/4, offset=(-s, -d + s, -h / 2), id=2, fullscreen=True, vsync=None, square_side=5e-2, square_loc='ll')

    screens = [right_screen,left_screen]
    manager = launch_stim_server(screens)
        
    #manager.black_corner_square()
    manager.set_idle_background(0)
    manager.load_stim(name='SineGrating')
    manager.start_stim()
    sleep(5)
    manager.stop_stim()
    #manager.loop()


    #trajectory, duration = moving_square_map()
    #trajectory, duration = Loom()
    #manager = OptionParser().create_manager()
    #manager = launch_server(flystim.stim_server, setup_name='bruker')
    #manager.load_stim(name='MovingPatch', trajectory=trajectory)
    #sleep(2)
    #manager.start_stim()
    #sleep(duration)
    #manager.stop_stim()

if __name__ == '__main__':
    main()
