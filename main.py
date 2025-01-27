import eel
import time
from waveform import State, Tab, WF_Block_Collection, WF_Block_Constant, WF_Block_PUND, WF_Block_Sine


eel.init('web')
state = State()

@eel.expose
def py_new_tab(id, name):
    tab = Tab(id, name)
    state.add_child(tab)
    tab.add_child(WF_Block_Collection()) # CH1
    tab.add_child(WF_Block_Collection()) # CH2
    
@eel.expose
def py_close_tab(id):
    state.remove_child_by_id(id)

@eel.expose
def py_delete_wf_block(tabId:str, channel:int, blockIdx:int):
    tab = state.find_child_by_id(tabId)
    tab[channel].pop(blockIdx)    

@eel.expose
def py_new_wf_block(tabId:str, channel:int, block_type:str):
    tab = state.find_child_by_id(tabId)
    collection = tab[channel-1]
    if block_type == 'pund':
        collection.add_child( WF_Block_PUND(amplitude=1.0, rise_time=350e-6, delay_time=350e-6, n_cycles=4., offset=0.) )
    else:
        raise NotImplementedError(f'Block of type {block_type} not supported.')

@eel.expose
def py_get_wf_block_settings(tabId:str, channel:int, blockIdx:int):
    tab = state.find_child_by_id(tabId)
    block = tab[channel-1][blockIdx]
    res = block.to_dict()
    return res
@eel.expose
def py_set_wf_block_settings(tabId:str, channel:int, blockIdx:int, blockSettings:dict):
    tab = state.find_child_by_id(tabId)
    print(blockSettings)
    tab[channel-1][blockIdx] = tab[channel-1][blockIdx].__class__.from_dict(blockSettings)

@eel.expose
def py_get_wf_skeleton(tabId):
    tab = state.find_child_by_id(tabId)
    
    data = []
    for ch in range(2):
        t,v = tab[ch].get_skeleton()
        data.append({'x':t.tolist(), 'y':v.tolist(), 
                     'type':'scatter', 'name':f'Ch{ch+1}'}) #plotly structure
    print(data)
    return data

@eel.expose
def py_connect():
    # Logic to copy CH1 to CH2
    print('In connect!')
    time.sleep(5)
    print('connect done!')
    return 0

@eel.expose
def py_upload():
    print('In send!')
    return 0

@eel.expose
def py_trigger():
    print('In trigger!')
    return 0


eel.start('main.html', close_callback=lambda e1,e2: print(state.to_dict()))
