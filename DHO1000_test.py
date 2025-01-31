# DHO1000_test.py
# Author: Tristan O'Neill
# Adapted from matlab code written by Yueyun Chen
import pyvisa, time
import numpy as np
from matplotlib import pyplot as plt

def determine_sample_rate(hscale, memorydepth):
    # determine the actual sampling rate accroding to the sweep mode
    return 1e9 # idk what YC's code does here so I'm just returning something

def identify(oscope):
    return oscope.query('*IDN?')

def reset(oscope):
    cmds = ['*RST']
    cmds.extend([f':chan{i}:disp 0' for i in range(4)]) # turn off all channels. *RST might do this?
    send(oscope, cmds)

def hconfig(oscope, hscale, memorydepth=10e6, trigoffset=0):
    '''All channels share horizontal configuration'''
    cmds = []
    cmds.append(":tim:roll 0") # turn off roll mode to enable trigger for time scale greater than 50 ms/div
    cmds.append(f":tim:main:scal {hscale}") # set time scale, s/div
    cmds.append(f":acq:mdep {memorydepth}") # set memory depth, Sa

    fs = determine_sample_rate(hscale, memorydepth) # determine the actual sampling rate, Sa/s

    # make sure trigger position doesn't fall into 0-1% of horizontal scale (s/div) in slow sweep mode
    # as of 2024/12/19, that will cause the oscilloscope to not trigger due to firmware bug
    # if trigoffset > 0 and hscale >= self.slow_sweep:
    #     trigoffset  = max(trigoffset,hscale*0.01)

    cmds.append(f":tim:main:offs {memorydepth/fs/2-trigoffset}") # set horizontal offset, seconds

    send(oscope, cmds)

def vconfig(oscope,channel:int, vscale, voffset, triglvl=0.5, trigsrc='EXT'):
    cmds = []
    cmds.append(f':chan{channel}:disp 1') # turn on channel
    cmds.append(f":chan{channel}:scal {vscale}") # set vertical scale, V/div
    cmds.append(f":chan{channel}:offs {voffset}") # set vertical offset, V

    # trigger settings
    # trigger source should be set to EXT for software trigger as well to avoid problems
    # trigger output is always enabled by default 
    cmds.append(f":trig:edge:sour {trigsrc}") # edge mode trigger source, use EXT for software trigger
    cmds.append(f":trig:edge:lev {triglvl}") # set trigger level

    # initiate single acquisition
    cmds.append(":stop") # stop the oscilloscope for single acquisition
    cmds.append(":single") # single acquisition mode

    send(oscope,cmds)

def send(oscope,cmds):
    # send all the commands
    for cmd in cmds:
        oscope.write(cmd) # 1 s delay might be necessary for the oscilloscope to be ready for recieving trigger
        time.sleep(0.2)

def force_trigger(oscope):
    # send software trigger and wait for acquisition to finish
    hscale = oscope.query(":tim:main:scal?") # query the horizontal scale, seconds
    time.sleep(1)
    oscope.write(":tforce") # send software trigger, no OPC query

def get_data(oscope, timeout=3):
    res = oscope.query(":trig:stat?")
    print(res)
    if 'STOP' not in res: # check if acquisition finished
        print(f"Acquisition not finished, data transfer will time out in {timeout} sec!")
        time.sleep(timeout)
        
        res = oscope.query(":trig:stat?")
        print(res)
        
        if 'STOP' not in res: # check if acquisition finished
            print("Data transfer not started due to incomplete acquisition!")
            return
        else:
            print("Acquisition finished, proceed to data transfer!")
    
    # read memory depth
    pts = int(float(oscope.query(":acq:mdep?").strip()))

    # determine active vertical channels
    active_ch = []
    for ch in range(1,5): # channels are indexed from 1, not 0
        if '1' in oscope.query(f":chan{ch}:disp?"):
            active_ch.append(ch)
    assert len(active_ch) > 0, 'No channels are being read!'

    # initialize waveform buffer and waveform info table
    # wf_buffer = np.zeros((len(active_ch),pts), dtype=np.uint16)
    wf_info = {ch:dict(samples=pts) for ch in active_ch}

    # read active channel's vertical information
    for i,ch in enumerate(active_ch):
        cmds = [] # initialize command array
        cmds.append(f":wav:sour CHAN{ch}") # source channel
        cmds.append(":wav:mode RAW") # read data from memory
        cmds.append(":wav:form WORD") # set waveform data to word (16-bit), or byte (8-bit)
        cmds.append(f":wav:stop {pts}") # set data reading stop point
        send(oscope, cmds)

        wf_info[ch]['raw_data'] = np.array(oscope.query_binary_values(":wav:data?", datatype='H'), dtype=np.uint16) # read data, no OPC command. H means unsigned short (16 bits)

        wf_info[ch]['y_increment'] = float(oscope.query(":wav:yinc?").strip()) # read y-increment, V/ADU
        wf_info[ch]['y_reference'] = float(oscope.query(":wav:yref?").strip()) # read y-reference, ADU, where the middle level is
        wf_info[ch]['y_origin'] = float(oscope.query(":wav:yor?").strip()) # # read y-origin, ADU, relative to the middle level
        print(wf_info[ch]['y_increment'], wf_info[ch]['y_reference'], wf_info[ch]['y_origin'], type(wf_info[ch]['y_origin']))
        wf_info[ch]['y_offset'] = (wf_info[ch]['y_reference']+wf_info[ch]['y_origin'])*wf_info[ch]['y_increment'] # y-offset, V
        
        # read horizontal information (xinc,xor), not channel-specific but I will save it that way anyway because it will make life easier
        wf_info[ch]['x_increment'] = float(oscope.query(":wav:xinc?").strip()) # read x-increment, s
        wf_info[ch]['x_offset'] =    float(oscope.query(":wav:xor?" ).strip()) # read x-offset, s. Time of the first point related to the trigger position            

    return wf_info

def wf_data_to_volts(raw_data, x_increment, x_offset, y_increment, y_offset, **unused_kwargs):
    t = np.arange(len(raw_data))*x_increment + x_offset
    volt = raw_data.astype(float)*y_increment + y_offset
    return t,volt


if __name__ == '__main__':
    rm = pyvisa.ResourceManager()

    with rm.open_resource('TCPIP0::10.97.108.205::INSTR') as oscope:
        print( identify(oscope) )

        reset(oscope)
        vconfig(oscope, channel=1, vscale=0.1, voffset=0)
        vconfig(oscope, channel=2, vscale=0.1, voffset=0)
        vconfig(oscope, channel=3, vscale=0.1, voffset=0)
        hconfig(oscope, hscale=1e-6, memorydepth=10e6)

        force_trigger(oscope)

        wf_info = get_data(oscope)

        for ch, wf_data in wf_info.items():
            plt.plot(*wf_data_to_volts(**wf_data), label=f'ch{ch}')
        plt.legend()
        plt.show()
