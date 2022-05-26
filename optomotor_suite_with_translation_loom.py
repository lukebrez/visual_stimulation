import socket
from flystim.stim_server import launch_stim_server
from flyrpc.transceiver import MySocketClient
import flyrpc.multicall
from flystim.screen import Screen
from time import sleep
from visprotocol.device import niusb
import random
import h5py
import numpy as np
import time
import os
from random import sample

use_bruker_server = True

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

period = 60
rate = 60
offsets = []
rotation_0 = {'name': 'RotatingGrating', 'angle': 0, 'period': period, 'rate': rate, 'color': 1, 'hold_duration': .5, 'phi': -45, 'offset': 180}
rotation_180 = {'name': 'RotatingGrating', 'angle': 180, 'period': period, 'rate': rate, 'color': 1, 'hold_duration': .5,'phi': -45, 'offset': 0}
long_grey = {'name': 'ConstantBackground'}
long_grey_dur = 60

loom_trajectory = {'name': 'Loom', 'rv_ratio': 0.02, 'stim_time': .75, 'start_size': 0, 'end_size': 180}
loom_stim = {'name': 'MovingSpot', 'radius': loom_trajectory, 'sphere_radius': 1, 'color': 0, 'theta': 0, 'phi': 0}

#################
### SET THESE ###
#################

stim_time = 0.75 #0.5 will be in hold
post_time = 1.25
# How long should a cluster of epochs be?
epoch_cluster_duration = 6.25 #in min # THIS IS SET BASED ON 5 1MIN GREY PERIODS AND 4 STIM PERIODS FOR 30MIN TOTAL
epoch_cluster_duration *= 60 # now in sec

###############################################
### CREATE LONG LIST OF ALL STIM TO PRESENT ###
###############################################

epoch_duration = post_time + stim_time
# given the duration of a single epoch and a cluster of epochs, how many epochs to present?
num_epochs_in_cluster = int(epoch_cluster_duration / epoch_duration)
num_single_stim_type = int(num_epochs_in_cluster/4) # divide by 4 because we have left and right movement, and translation, and loom

epoch_cluster_list = []
for i in range(num_single_stim_type):
    ### adding translation key. will remove below before passing to flystim
    stim = rotation_0.copy()
    stim['Translation']=False
    epoch_cluster_list.append(stim)

    stim = rotation_180.copy()
    stim['Translation']=False
    epoch_cluster_list.append(stim)

    stim = rotation_0.copy()
    stim['Translation']=True
    epoch_cluster_list.append(stim)

    stim = loom_stim.copy()
    stim['Translation']=False
    epoch_cluster_list.append(stim)

random.shuffle(epoch_cluster_list)

### Shuffle phase to avoid spatial clustering in optic lobes
phase_offsets = list(np.arange(0,360,20)) # sample every 20 degrees
for i in range(len(epoch_cluster_list)):
    if epoch_cluster_list[i]['name'] == 'RotatingGrating':
        random_offset = int(sample(phase_offsets,1)[0]) # add random offset
        epoch_cluster_list[i]['offset'] += random_offset

##################
### Save order ###
##################

### extract metadata
angles = []
offsets = []
translation = []
names = []
for stim in epoch_cluster_list:
    angles.append(stim.get('angle', np.nan))
    offsets.append(stim.get('offset', np.nan))
    translation.append(stim.get('Translation', np.nan))
    names.append(stim.get('name'))

### save to hdf5
save_file = os.path.join('.', time.strftime("%Y%m%d-%H%M%S") + '.hdf5')
with h5py.File(save_file,'w') as h5:
    h5.create_dataset("data", data=np.asarray(angles)) # keeping "data" for backwards compatability
    h5.create_dataset("angle", data=np.asarray(angles))
    h5.create_dataset("offset", data=np.asarray(offsets))
    h5.create_dataset("translation", data=np.asarray(translation))
    h5.create_dataset("name", data=names)

#######################################################
### CONCATENATE EPOCH CLUSTERS BETWEEN GREY PERIODS ###
#######################################################

epoch_cluster_list.insert(0,long_grey)
epoch_cluster_list = epoch_cluster_list + epoch_cluster_list + epoch_cluster_list + epoch_cluster_list
epoch_cluster_list.append(long_grey)

######################
### Trigger Bruker ###
######################

# Send triggering TTL through the NI-USB device (if device is set)
if niusb_device is not None:
    niusb_device.sendTrigger()

#######################
### DISPLAY STIMULI ###
#######################

for stim in epoch_cluster_list:


    # pop will remove this key from the dict as well
    # this is good because flystim will not recognize this key
    translation = stim.pop('Translation', None)
    manager.load_stim(name='ConstantBackground', color=[0.5, 0.5, 0.5, 1.0], side_length=100) #this is necessary for loom
    manager.load_stim(**stim, hold=True)
    #manager.load_stim(name='MovingSpot', radius=loom_trajectory, sphere_radius=1, color=0, theta=0, phi=0, hold=True)

    if translation:
        stim['angle'] -= 180
        #stim['offset'] = 180
        #stim['color'] = [1, 0, 1, 1]
        stim['cylinder_location'] = (-.001,0,0)
        manager.load_stim(**stim, hold=True)

    multicall = flyrpc.multicall.MyMultiCall(manager)
    multicall.start_corner_square()
    multicall.start_stim()
    multicall()

    if stim['name'] == 'ConstantBackground':
        sleep(long_grey_dur)
    else:
        sleep(stim_time)

    multicall = flyrpc.multicall.MyMultiCall(manager)
    multicall.stop_stim()
    multicall.black_corner_square()
    multicall()
    sleep(post_time)
