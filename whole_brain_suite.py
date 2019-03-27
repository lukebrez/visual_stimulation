#!/usr/bin/env python3

from math import pi, sqrt
from time import sleep
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.dlpc350 import make_dlpc350_objects

from flystim.trajectory import RectangleTrajectory, Trajectory
from luke_stim import stim_builder
from luke_stim_types import *

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
    eye_correction = 0 #10e-3

    right_screen = Screen(width=w, height=h, rotation=+pi/4, offset=(+s+eye_correction, -d + s, -h / 2), id=1, fullscreen=True, vsync=None, square_side=5e-2, square_loc='lr')
    left_screen = Screen(width=w, height=h, rotation=-pi/4, offset=(-s-eye_correction, -d + s, -h / 2), id=2, fullscreen=True, vsync=None, square_side=5e-2, square_loc='ll')

    screens = [right_screen,left_screen]
    manager = launch_stim_server(screens)

    #Get duration of desired trajectory
    #MovingSquareMap_kwargs = {'name': 'MovingSquareMap', 'azimuth_max': 180,
    #                          'azimuth_min': 0, 'elevation_max': 180, 'elevation_min': 90,
    #                          'square_width': 10, 'velocity': 400}
    #_, duration_map = MovingSquareMap(**MovingSquareMap_kwargs)


    #loom_kwargs = {'name': 'Loom', 'center_x': 90, 'center_y': 90,
    #               'start_width': 0, 'end_width': 90, 'velocity': 60}
    #_, duration_loom = Loom(**loom_kwargs)

    #define desired stimuli
    #stimuli = [{'kwargs': {'name': 'RotatingBars', 'angle': 0},'duration': 1e3},
    #           {'kwargs': MovingSquareMap_kwargs, 'duration': duration_map},
    #           {'kwargs': loom_kwargs, 'duration': duration_loom}]

    master_dur = 20e3
    master_per = 20
    master_rate = 1
    stimuli = [{'kwargs': {'name': 'SineGrating', 'angle': 0, 'period': master_per, 'rate': master_rate},'duration': master_dur},
               {'kwargs': {'name': 'SineGrating', 'angle': 90, 'period': master_per, 'rate': master_rate},'duration': master_dur},
               {'kwargs': {'name': 'SineGrating', 'angle': 180, 'period': master_per, 'rate': master_rate},'duration': master_dur},
               {'kwargs': {'name': 'SineGrating', 'angle': 270, 'period': master_per, 'rate': master_rate},'duration': master_dur}]
    
    #get experiment stimuli sequence and durations
    stims, dur = stim_builder(stimuli,
                              imaging_rate = 2.145, #in Hz
                              num_blocks = 5,
                              approx_exp_dur = 30, #in minutes
                              inter_block_dur = 2, #in sec
                              post_stim_dur = 2e3, #in ms
                              inter_stim_id = {'name': 'Grey'},
                              path = '/home/clandininlab/luke_data')
    dur = [ _/1000 for _ in dur]

    manager.white_corner_square()
    manager.set_idle_background(0.5)
    sleep(2)

    for i, stim in enumerate(stims):
        print(stim)

        if stim['name'] == 'Grey':
            manager.black_corner_square()
            sleep(dur[i])
        elif stim['name'] == 'MovingSquareMap':
            trajectory, _ = MovingSquareMap(**stim)
            manager.load_stim(name='MovingPatch', trajectory=trajectory)
            manager.start_corner_square()
            manager.start_stim()
            sleep(dur[i])
            manager.stop_stim()
        elif stim['name'] == 'Loom':
            trajectory, _ = Loom(**stim)
            manager.load_stim(name='MovingPatch', trajectory=trajectory)
            manager.start_corner_square()
            manager.start_stim()
            sleep(dur[i])
            manager.stop_stim()
        else:
            manager.load_stim(**stim)
            manager.start_corner_square()
            manager.start_stim()
            sleep(dur[i])
            manager.stop_stim()

if __name__ == '__main__':
    main()
