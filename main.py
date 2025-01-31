import eel, os, pyvisa, json, sys, time, pprint
from app_base import (AppState, Tab,
                      DUTSettings,
                      AWGChannelSettings, AWGSettings,
                      OscilloscopeChannelSettings, OscilloscopeSettings,)
from templatewf import wf_class_dict


STATEDIR = './.states/'
state:AppState
try:
    rm = pyvisa.ResourceManager()
except:
    rm = None

eel.init('web')


@eel.expose
def py_update_state(d:dict|None=None):
    global state
    if d is None:
        if not os.path.exists(STATEDIR):
            os.mkdir(STATEDIR)
        state_files = sorted([f for f in os.listdir(STATEDIR) if os.path.isfile(os.path.join(STATEDIR,f))])
        if len(state_files) > 0:
            with open(os.path.join(STATEDIR,state_files[-1])) as f:
                state = AppState.from_dict(json.load(f))
        else:
            state = AppState()
    else:
        state = AppState.from_dict(d)
    return state.to_dict() # return so that frontend has inputs, corrected
@eel.expose
def py_get_available_resources():
    if rm is None:
        return []
    else:
        return rm.list_resources()

@eel.expose
def py_new_tab(d:dict):
    tab = Tab.from_dict(d)
    state.add_child(tab)

@eel.expose
def py_close_tab(id):
    state.remove_child_by_id(id)

@eel.expose
def py_new_wf_block(tabId:str, channel:int, block_type:str):
    tab = state.find_child_by_id(tabId)
    collection = tab[channel-1]
    collection.add_child( wf_class_dict[block_type]() )
@eel.expose
def py_delete_wf_block(tabId:str, channel:int, blockIdx:int):
    tab = state.find_child_by_id(tabId)
    tab[channel-1].pop(blockIdx)
@eel.expose
def py_swap_wf_blocks(tabId:str, channel:int, blockIdx0:int, blockIdx1:int):
    tab = state.find_child_by_id(tabId)
    tab[channel-1].swap_children(blockIdx0, blockIdx1)

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
    return data

@eel.expose
def py_connect():
    # Logic to copy CH1 to CH2
    print('In connect!')
    time.sleep(5)
    print('connect done!')
    return 0

@eel.expose
def py_send_waveform(tabId:str): # returns True if waveform upload was successful. False otherwise.
    return True

@eel.expose
def py_trigger():
    print('In trigger!')
    return 0

def close(*args, **kwargs):
    d = state.to_dict()
    # print('Application state upon closing:')
    # pprint.pprint(d)

    ofname = f'{STATEDIR}/app-state-{time.time()}.json'
    if not os.path.exists(STATEDIR):
        os.mkdir(STATEDIR)
    # with open(ofname, 'w') as f:
    #     json.dump(d, f, indent=4)
    
    # print(f'State saved to {ofname}')
    sys.exit()


eel.start('main.html', mode='edge', close_callback=close)
