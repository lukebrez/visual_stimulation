import numpy as np
import sys
import random
import matplotlib.pyplot as plt
import os
from time import strftime

def stim_builder(stimuli, imaging_rate, num_blocks, approx_exp_dur,
                 inter_block_dur, post_stim_dur, inter_stim_id, path):

    seed = random.randrange(1234567890)
    stimuli_master = []
    time = 0

    all_stim_dur = sum(_['duration'] for _ in stimuli) #add durations of all stimuli together
    all_grey_stim_dur = len(stimuli) * post_stim_dur #total time of grey for one stim cycle
    all_inter_block_grey_dur = (num_blocks + 1) * inter_block_dur #total time of grey between blocks

    block_dur = (approx_exp_dur * 60 - all_inter_block_grey_dur / 1e3) / num_blocks #duration of one block

    #how many times each stim can be displayed in a block
    num_cycles = int(np.floor(block_dur / (all_stim_dur / 1e3 + all_grey_stim_dur / 1e3)))

    #amount to shift stimulus onset relative to imaging to end up with even imaging coverage for each stimuli
    shift_len = (1 / imaging_rate) / num_cycles

    #set random state
    r = np.random.RandomState(seed)

    stimuli_master.append((inter_stim_id, time)) #add grey
    time += inter_block_dur * 1e3 #update time based on inter block duration

    #create list of desired shifts (these shifts evenly cover the space between imaging time points)
    shifts_master = [num * (shift_len * 1e3) for num in list(range(1,num_cycles))]

    #should each block have the same exact stimtime/imaging time shift? I think I will try without that.

    for block in range(num_blocks):
        #create a list of shuffled stimuli ids
        stim_ids = list(range(len(stimuli)))
        stim_ids_shuff_first = list(r.permutation(stim_ids))

        first_stim = []

        #append first cycle of stimuli 
        for i in stim_ids_shuff_first:
            stimuli_master.append((stimuli[i]['kwargs'], time))
            first_stim.append((stimuli[i]['kwargs'], time))
            time += stimuli[i]['duration']
            stimuli_master.append((inter_stim_id, time))
            time += post_stim_dur

        #Each stimuli needs a random version of shifts_master
        shifts_shuff = []
        shifts_shuff.append([list(r.permutation(shifts_master)) for stim in range(len(stimuli))])
        shifts_shuff = shifts_shuff[0] #remove outer added list layer
        #now shifts_shuff[i] gives the stimulus order for the ith stimuli

        for cycle in range(num_cycles-1):
            stim_ids_shuff = list(r.permutation(stim_ids))
            for stim in stim_ids_shuff:
                #find index for the desired stim in the first stim list
                stim_loc = int(np.where(np.asarray(stim_ids_shuff_first) == stim)[0])

                #find time the stim was first displayed
                stim1 = first_stim[stim_loc][1]

                #based on imaging rate, if stim were displayed now, calculate the stim offset from its first display
                stim_offset = (time - stim1) % (1 / imaging_rate * 1e3)

                #how much grey delay to add
                delay_to_add = shifts_shuff[stim][cycle] - stim_offset

                if delay_to_add < 0:
                    delay_to_add += 1 / imaging_rate * 1e3

                time += delay_to_add

                stimuli_master.append((stimuli[stim]['kwargs'], time))

                time += stimuli[stim]['duration']
                stimuli_master.append((inter_stim_id, time))
                time += post_stim_dur
                
        stimuli_master.append((inter_stim_id, time)) #add inter block grey
        time += inter_block_dur * 1e3 #update time based on inter block duration
        time += r.randint(0,2000) #extend grey by random amount - keeps blocks independent
    
    times = [ _[1] for _ in stimuli_master]
    dur = list(np.diff(times))
    dur.append(inter_block_dur * 1e3)
    stim = [ _[0] for _ in stimuli_master]

    folder = 'exp-' + strftime('%Y%m%d-%H%M%S')
    exp_dir = os.path.join(path, folder)
    os.makedirs(exp_dir)

    np.save(os.path.join(exp_dir, 'stimuli_master'), stimuli_master)
    np.savetxt(os.path.join(exp_dir, 'stim.txt'), stim, fmt = '%s')
    np.savetxt(os.path.join(exp_dir, 'dur.txt'), dur)

    metaDict = {}
    metaDict['imaging_rate'] = imaging_rate
    metaDict['num_blocks'] = num_blocks
    metaDict['requested_exp_dur (min)'] = approx_exp_dur
    metaDict['inter_block_dur (sec)'] = inter_block_dur
    metaDict['post_stim_dur (ms)'] = post_stim_dur
    metaDict['inter_stim_id'] = inter_stim_id
    metaDict['num_cycles (calc)'] = num_cycles
    metaDict['block_dur (calc)'] = block_dur
    metaDict['shifts_master (calc)'] = shifts_master
    metaDict['actual_exp_dur (min) (calc)'] = (times[-1] + inter_block_dur * 1e3) / 1000 / 60

    f = open(os.path.join(exp_dir,'meta.txt'),'w')
    print(exp_dir)
    for k, v in metaDict.items():
        f.write(str(k) + ' >>> '+ str(v) + '\n\n')

    return(stim, dur)
