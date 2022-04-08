import socket
from flystim.stim_server import launch_stim_server
from flyrpc.transceiver import MySocketClient
from flystim.screen import Screen
from time import sleep
from visprotocol.device import niusb
import random
import h5py
import numpy as np
import time
import os

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

###################### DEFINE STIMULI ############################

period = 60
rate = 60
rotation_0 = {'name': 'RotatingGrating', 'angle': 0, 'period': period, 'rate': rate, 'color': 1, 'hold_duration': .5, 'phi': -45, 'offset': 180}
rotation_180 = {'name': 'RotatingGrating', 'angle': 180, 'period': period, 'rate': rate, 'color': 1, 'hold_duration': .5,'phi': -45}
long_grey = {'name': 'ConstantBackground'}
long_grey_dur = 60

########################  SET THESE ############################

stim_time = 0.75 #0.5 will be in hold
post_time = 1.25
# How long should a cluster of epochs be?
epoch_cluster_duration = 6.25 #in min # THIS IS SET BASED ON 5 1MIN GREY PERIODS AND 4 STIM PERIODS FOR 30MIN TOTAL
epoch_cluster_duration *= 60 # now in sec

######################   CREATE LONG LIST OF ALL STIM TO PRESENT   ########################

epoch_duration = post_time + stim_time
# given the duration of a single epoch and a cluster of epochs, how many epochs to present?
num_epochs_in_cluster = int(epoch_cluster_duration / epoch_duration)
num_single_stim_type = int(num_epochs_in_cluster/2) # just divide in 2 because we have left and right movement

epoch_cluster_list = []
for i in range(num_single_stim_type):
	epoch_cluster_list.append(rotation_0)
	epoch_cluster_list.append(rotation_180)

random.shuffle(epoch_cluster_list)

### Save order ###
angles = []
for stim in epoch_cluster_list:
	angles.append(stim['angle'])
save_file = os.path.join('.', time.strftime("%Y%m%d-%H%M%S") + '.hdf5')
with h5py.File(save_file,'w') as h5:
	h5.create_dataset("data", data=np.asarray(angles))

### CONCATENATE EPOCH CLUSTERS BETWEEN GREY PERIODS 
epoch_cluster_list.insert(0,long_grey)
epoch_cluster_list = epoch_cluster_list + epoch_cluster_list + epoch_cluster_list + epoch_cluster_list
epoch_cluster_list.append(long_grey)

# Send triggering TTL through the NI-USB device (if device is set)
if niusb_device is not None:
	niusb_device.sendTrigger()


########################## DISPLAY STIMULI #####################################
for stim in epoch_cluster_list:
	manager.load_stim(**stim)
	manager.start_corner_square()
	manager.start_stim()
	if stim['name'] == 'ConstantBackground':
		sleep(long_grey_dur)
	else:
		sleep(stim_time)
	manager.stop_stim()
	manager.black_corner_square()
	sleep(post_time)
