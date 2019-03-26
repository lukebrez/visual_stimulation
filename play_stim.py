#!/usr/bin/env python3

# Example client program that walks through all available stimuli.

from time import sleep
#from flystim.options import OptionParser
from flyrpc.launch import launch_server
from luke_stim_types import *

def main():
    #trajectory, duration = moving_square_map()
    trajectory, duration = Loom()
    #manager = OptionParser().create_manager()
    manager = launch_server(flystim.stim_server, setup_name='bruker')
    manager.load_stim(name='MovingPatch', trajectory=trajectory)
    sleep(2)
    manager.start_stim()
    sleep(duration)
    manager.stop_stim()

if __name__ == '__main__':
    main()
