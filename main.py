import eel, os, pyvisa, json, sys, time, pprint
from app_base import (AppState, Tab,
                      DUTSettings,
                      AWGChannelSettings, AWGSettings,
                      OscilloscopeChannelSettings, OscilloscopeSettings,
                      base_class_dict)
from templatewf import wf_class_dict, CollectionTemplateWF

STATEDIR = './.states/'
state:AppState = None
try:
    rm = pyvisa.ResourceManager()
except:
    rm = None

eel.init('web')


@eel.expose
def py_update_state(d:dict|None=None):
    '''Update the state in the backend using a dict created by the frontend.'''
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
    return state.to_dict()
    

@eel.expose
def py_get_available_resources():
    if rm is None:
        return []
    else:
        return rm.list_resources()

@eel.expose
def py_update_frontend(py_id:int):
    print(py_id)
    elem = state.find_by_py_id(int(py_id))
    elem.apply( lambda elem: eel.js_update_frontend(elem.selector, {k:e for k,e in elem.to_dict().items() if (k != 'children' and k != '_type')}) )
@eel.expose
def py_update_backend(py_id:int, d:dict):
    print('Updating', py_id, d)
    d.pop('py_id', '')
    d.pop('pyclassname', '')
    state.find_by_py_id(int(py_id)).update(**d)

@eel.expose
def py_new_tab(id:str, name:str):
    # fresh tab. State->Tab->[AWG->[AWGchannels->WFs], Oscope->[OscopeChannels]]
    tab:Tab = Tab(id=id, name=name)
    state.add_child(tab)
    
    awg = AWGSettings()
    tab.add_child( awg )

    for i in [1,2]:
        awgch = AWGChannelSettings(channel=i)
        awg.add_child(awgch)
        awgch.add_child(CollectionTemplateWF())
    
    oscope = OscilloscopeSettings()
    tab.add_child(oscope)
    
    for i in [1,2,3,4]:
        oscope.add_child(OscilloscopeChannelSettings(channel=i))
    
    return tab.py_id
    tab.apply( lambda elem: eel.js_update_frontend(elem.selector, {k:e for k,e in elem.to_dict().items() if (k != 'children' and k!= '_type')}) )


@eel.expose
def py_delete_element(py_id:int):
    elem = state.find_by_py_id(py_id)
    elem.parent.pop( elem.parent._children.index(elem) )


@eel.expose
def py_new_wf_block(parent_py_id:int, wfType:str):
    print(wfType, parent_py_id)
    collection = state.find_by_py_id(int(parent_py_id))
    newblock = wf_class_dict[wfType]()
    collection.add_child( newblock )
    return newblock.py_id
@eel.expose
def py_move_child_elem(parent_py_id:int, child_py_id:int, shift:int):
    '''Rearrange order of children'''
    collection = state.find_by_py_id(int(parent_py_id))
    child = state.find_by_py_id(int(child_py_id))
    idx = collection._children.index(child)
    collection[idx], collection[idx-int(shift)] = collection[idx-int(shift)], collection[idx]
    
@eel.expose
def py_get_wf_block_settings(py_id:int):
    block = state.find_by_py_id(py_id)
    return block.to_dict()
@eel.expose
def py_set_wf_block_settings(py_id:int, blockSettings:dict):
    block = state.find_by_py_id(py_id)
    block.update(**blockSettings)
    eel.js_update_frontend(py_id, block.py_id)
    

@eel.expose
def py_get_wf_skeleton(awgsettings_py_id):
    '''Given the py_id for an AWGSettings object, returns the wf template skeleton (minimally sampled)'''
    awg = state.find_by_py_id(awgsettings_py_id)
    assert isinstance(awg, AWGSettings), f'Expected a py_id for an AWGSettings, but got {type(awg)}'
    data = []
    for chan in awg._children:
        t,v = chan[0].get_skeleton()
        data.append({'x':t.tolist(), 'y':v.tolist(), 
                    'type':'scatter', 'name':f'Ch{chan.channel+1}'}) #plotly structure
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
    elem = state._children[0]._children[1].selector
    eel.js_update_frontend(elem, {"sample_rate": 1e9})
    return True

@eel.expose
def py_trigger():
    print('In trigger!')
    return 0

def on_close(*args, **kwargs):
    d = state.to_dict()
    print('Application state upon closing:')
    pprint.pprint(d)

    ofname = f'{STATEDIR}/app-state-{time.time()}.json'
    if not os.path.exists(STATEDIR):
        os.mkdir(STATEDIR)
    # with open(ofname, 'w') as f:
    #     json.dump(d, f, indent=4)
    
    # print(f'State saved to {ofname}')
    sys.exit()


eel.start('main.html', mode='edge', close_callback=on_close)
