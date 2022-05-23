import socket
from flyrpc.transceiver import MySocketClient
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import Trajectory
from time import sleep
from visprotocol.device import niusb
import random
import h5py
import numpy as np
import time
import os
from random import sample

use_bruker_server = False

if use_bruker_server:
	host = '171.65.17.246'
	port = 60629
	manager = MySocketClient(host=host, port=port)
	niusb_device = niusb.NIUSB6210(dev='Dev5', trigger_channel='ctr0')
else:
	aux_screen = Screen(id=0, fullscreen=False, vsync=True, square_size=(0.25, 0.25))
	manager = launch_stim_server(aux_screen)
	niusb_device = None

manager.black_corner_square()
manager.set_idle_background(0.5)

######################
### DEFINE STIMULI ###
######################

#period = 60
#rate = 60
# offsets = []
#rotation_0 = {'name': 'RotatingGrating', 'angle': 0, 'period': period, 'rate': rate, 'color': 1, 'hold_duration': .5, 'phi': -45, 'offset': 180}
# rotation_180 = {'name': 'RotatingGrating', 'angle': 180, 'period': period, 'rate': rate, 'color': 1, 'hold_duration': .5,'phi': -45, 'offset': 0}
# long_grey = {'name': 'ConstantBackground'}
# long_grey_dur = 1#60
# stim = rotation_0
# stim_time = 3
# post_time = 3

#######################################

# manager.load_stim(name='ConstantBackground', color=[.5, .5, .5, 1], side_length=100)
# manager.start_stim()
# sleep(2)

# '''issues:
#  - wrong shape
#  - grey end screen
#  - loom un-looms (whhaaaaaa????)
# '''

# loom_trajectory = {'name': 'Loom',
#                    'rv_ratio': .04,
#                    'stim_time': 1,
#                    'start_size': 40,
#                    'end_size': 50} #78
# #https://github.com/ClandininLab/flystim/blob/442c97b01c6c8f472a7e80110b678d2a326e0442/flystim/trajectory.py#L26

# #moving spot calls make_as_trajectory on radius

# manager.load_stim(name='MovingSpot', radius=loom_trajectory, sphere_radius=1, color=0, theta=0, phi=0, hold=True)

# manager.start_stim()
# manager.start_corner_square()
# sleep(4)
# manager.stop_stim()
# manager.black_corner_square()
# sleep(5)

#######################################

manager.load_stim(name='ConstantBackground', color=[0.5, 0.5, 0.5, 1.0], side_length=100)

loom_trajectory = {'name': 'Loom',
                   'rv_ratio': 0.08,
                   'stim_time': 4,
                   'start_size': 3,
                   'end_size': 90}

# loom_trajectory = {'name': 'Loom',
#                    'rv_ratio': 0.08,
#                    'stim_time': 2,
#                    'start_size': 3,
#                    'end_size': 90}

color_trajectory = {'name': 'Sinusoid',
                    'temporal_frequency': 2,
                    'amplitude': 1,
                    'offset': 1}

manager.load_stim(name='MovingSpot', radius=loom_trajectory, sphere_radius=1, color=0, theta=0, phi=0, hold=True)

sleep(1)

manager.start_stim()
sleep(4)

manager.stop_stim(print_profile=True)
sleep(1)

####################################### 

# #################
# ### SET THESE ###
# #################

# stim_time = 0.75 #0.5 will be in hold
# post_time = 1.25
# # How long should a cluster of epochs be?
# epoch_cluster_duration = 6.25 #in min # THIS IS SET BASED ON 5 1MIN GREY PERIODS AND 4 STIM PERIODS FOR 30MIN TOTAL
# epoch_cluster_duration *= 60 # now in sec

# ###############################################
# ### CREATE LONG LIST OF ALL STIM TO PRESENT ###
# ###############################################

# epoch_duration = post_time + stim_time
# # given the duration of a single epoch and a cluster of epochs, how many epochs to present?
# num_epochs_in_cluster = int(epoch_cluster_duration / epoch_duration)
# num_single_stim_type = int(num_epochs_in_cluster/2) # just divide in 2 because we have left and right movement

# epoch_cluster_list = []
# for i in range(num_single_stim_type):
# 	epoch_cluster_list.append(rotation_0.copy())
# 	epoch_cluster_list.append(rotation_180.copy())

# random.shuffle(epoch_cluster_list)

# ### Shuffle phase to avoid spatial clustering in optic lobes
# phase_offsets = list(np.arange(0,360,20)) # sample every 20 degrees
# for i in range(len(epoch_cluster_list)):
# 	if epoch_cluster_list[i]['name'] == 'RotatingGrating':
# 		random_offset = int(sample(phase_offsets,1)[0]) # add random offset
# 		epoch_cluster_list[i]['offset'] += random_offset

# ##################
# ### Save order ###
# ##################

# ### extract metadata
# angles = []
# offsets = []
# for stim in epoch_cluster_list:
# 	angles.append(stim['angle'])
# 	offsets.append(stim['offset'])

# ### save to hdf5
# save_file = os.path.join('.', time.strftime("%Y%m%d-%H%M%S") + '.hdf5')
# with h5py.File(save_file,'w') as h5:
# 	h5.create_dataset("data", data=np.asarray(angles)) # keeping "data" for backwards compatability
# 	h5.create_dataset("angle", data=np.asarray(angles))
# 	h5.create_dataset("offset", data=np.asarray(offsets))

# #######################################################
# ### CONCATENATE EPOCH CLUSTERS BETWEEN GREY PERIODS ###
# #######################################################

# epoch_cluster_list.insert(0,long_grey)
# epoch_cluster_list = epoch_cluster_list + epoch_cluster_list + epoch_cluster_list + epoch_cluster_list
# epoch_cluster_list.append(long_grey)

######################
### Trigger Bruker ###
######################

# # Send triggering TTL through the NI-USB device (if device is set)
# if niusb_device is not None:
# 	niusb_device.sendTrigger()

# #######################
# ### DISPLAY STIMULI ###
# #######################

# # for stim in epoch_cluster_list:
# manager.load_stim(**stim)
# manager.start_corner_square()
# manager.start_stim()
# if stim['name'] == 'ConstantBackground':
# 	sleep(long_grey_dur)
# else:
# 	sleep(stim_time)
# manager.stop_stim()
# manager.black_corner_square()
# sleep(post_time)

