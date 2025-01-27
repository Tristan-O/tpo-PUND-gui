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
def py_new_wf_block(tabId:str, channel:int, block_type:str, args_dict:dict):
    tab = state.find_child_by_id(tabId)
    collection = tab._children[channel]
    if block_type == 'pund':
        collection.add_child( WF_Block_PUND(**args_dict) )        
    else:
        raise NotImplementedError(f'Block of type {block_type} not supported.')
        

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
