#!/usr/bin/env python3

from time import sleep

from flystim.trajectory import RectangleTrajectory, Trajectory
from flyrpc.launch import launch_server
import flystim.stim_server
from luke_stim import stim_builder
from luke_stim_types import *

def main():
    manager = launch_server(flystim.stim_server, setup_name='bruker')
    #manager = OptionParser().create_manager()

    #Get duration of desired trajectory
    MovingSquareMap_kwargs = {'name': 'MovingSquareMap', 'azimuth_max': 180,
                              'azimuth_min': 0, 'elevation_max': 180, 'elevation_min': 90,
                              'square_width': 10, 'velocity': 400}
    _, duration_map = MovingSquareMap(**MovingSquareMap_kwargs)


    loom_kwargs = {'name': 'Loom', 'center_x': 90, 'center_y': 90,
                   'start_width': 0, 'end_width': 90, 'velocity': 60}
    _, duration_loom = Loom(**loom_kwargs)

    #define desired stimuli
    stimuli = [{'kwargs': {'name': 'RotatingBars', 'angle': 0},'duration': 1e3},
               {'kwargs': MovingSquareMap_kwargs, 'duration': duration_map},
               {'kwargs': loom_kwargs, 'duration': duration_loom}]
    
    #get experiment stimuli sequence and durations
    stims, dur = stim_builder(stimuli,
                              imaging_rate = 2.145, #in Hz
                              num_blocks = 5,
                              approx_exp_dur = 30, #in minutes
                              inter_block_dur = 2, #in sec
                              post_stim_dur = 2e3, #in ms
                              inter_stim_id = {'name': 'Grey'},
                              path = '~/luke_data')
    dur = [ _/1000 for _ in dur]

    manager.white_corner_square()
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
