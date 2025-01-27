import numpy as np


class State:
    '''This is the state of the app. Saves and loads from json. There should really only be one instance of State, but I won't enforce that.'''
    @classmethod
    def _get_all_subclasses(cls):
        '''Recursively get all subclasses of this class. This list includes this class.'''
        subclasses = [cls]
        for subclass in cls.__subclasses__():
            subclasses.extend(subclass._get_all_subclasses())
        return subclasses
    @staticmethod
    def from_dict(d:dict):
        '''Recursively load a state'''
        _type = d.pop('_type')
        children = d.pop('children', [])
        for cls in State._get_all_subclasses():
            if cls.__name__ == _type:
                this = cls(**d)
                for child in children:
                    this.add_child( cls.from_dict(child) )
                return this
        else:
            raise ValueError(f'{_type} is not a valid subclass of State!')
    def to_dict(self)->dict:
        return dict(_type=self.__class__.__name__,
                    children=[child.to_dict() for child in self._children])
    def __init__(self):
        self._children:list[State] = []
    def add_child(self, child):
        assert any([isinstance(child, cls) for cls in State.__subclasses__()]), f'Child must be an instance of a direct subclass of State, e.g. {State.__subclasses__()}'
        self._children.append(child)
    def pop(self, idx:int):
        return self._children.pop(idx)
    def __getitem__(self, idx:int):
        assert isinstance(idx, int), f'List_WF_Block only supports integer indexing right now. No slicing.'
        return self._children[idx]
    def __setitem__(self, idx:int, child):
        assert isinstance(idx, int), f'List_WF_Block only supports integer indexing right now. No slicing.'
        # assert isinstance(child, State), f'Expected WF_Block_Base, but got {type(child)} which does not inherit from Abstrack_WF_Block!'
        self._children[idx] = child
    def swap_children(self, idx1, idx2):
        self[idx1], self[idx2] = self[idx2], self[idx1]
    def find_child_by_id(self, id):
        for child in self._children:
            if child.id == id:
                return child
        else:
            raise ValueError(f'Child with id {id} not found!')
    def remove_child_by_id(self, id):
        for i,child in enumerate(self._children):
            if child.id == id:
                self._children.pop(i)
                break
        else:
            raise ValueError(f'Child with id {id} not found!')


class Tab(State):
    '''This class represents Tabs in the app.'''
    def __init__(self, id:str, name:str):
        super().__init__()
        self.id = id
        self.name = name
    def to_dict(self)->dict:
        res = dict(name=self.name, id=self.id)
        res.update( super().to_dict() )
        return res


class WF_Block_Base(State):
    '''Abstract base class instructions.'''
    def get_skeleton(self)->tuple[np.ndarray, np.ndarray]:
        raise NotImplementedError
    def get_time_array(self, sample_rate:float)->np.ndarray:
        '''Get an array of times corresponding to this block, for the specified sample rate'''
        raise NotImplementedError
    def sample_wf(self, sample_rate:float):
        '''Get an array of values corresponding to this block, for the specified sample rate'''
        raise NotImplementedError
    def add_child(self, child):
        raise NotImplementedError

class WF_Block_PUND(WF_Block_Base):
    '''A PUND waveform. If `ndpu`, multiplies by a -1. Equivalent to making the amplitude negative.
    Cannot have children.'''
    def to_dict(self):
        return dict(_type=self.__class__.__name__, 
                    amplitude=self.amplitude, 
                    rise_time=self.rise_time, 
                    delay_time=self.delay_time, 
                    n_cycles=self.n_cycles, 
                    offset=self.offset, 
                    ndpu=self.ndpu)
    def __init__(self, amplitude:float, rise_time:float, delay_time:float, n_cycles:float, offset:float, ndpu:bool):
        self.amplitude = amplitude
        self.rise_time = rise_time
        self.delay_time = delay_time
        self.n_cycles = n_cycles
        self.offset = offset
        self.ndpu = ndpu
    def get_time_array(self, sample_rate):
        return np.arange(0, self.n_cycles*(4*self.delay_time + 8*self.delay_time), 1/sample_rate)
    def sample_wf(self, sample_rate:float):
        time = self.get_time_array(sample_rate)
        quarter_PUND = lambda t, rise_time, period, quarter: np.abs((2 * (
                                                                    (t-period/4*quarter - period * np.floor((t-period/4*quarter) / (rise_time + period))) / rise_time -
                                                                    np.floor((t-period/4*quarter - period * np.floor((t-period/4*quarter) / (rise_time + period))) / rise_time + 0.5)))
                                                                ) * ((t-period/4*quarter) % (rise_time + period) < rise_time)
        pund = lambda t, rise_time, delay_time: + quarter_PUND(t, rise_time, rise_time*8+delay_time*4, 0) \
                                                + quarter_PUND(t, rise_time, rise_time*8+delay_time*4, 1) \
                                                - quarter_PUND(t, rise_time, rise_time*8+delay_time*4, 2) \
                                                - quarter_PUND(t, rise_time, rise_time*8+delay_time*4, 3)
        return self.offset + self.amplitude*pund(time, self.rise_time, self.delay_time)*(-1 if self.ndpu else 1)

class WF_Block_Sine(WF_Block_Base):
    '''A sine waveform.
    Cannot have children.'''
    def to_dict(self):
        return dict(_type=self.__class__.__name__, 
                    amplitude=self.amplitude,
                    freq=self.freq,
                    n_cycles=self.n_cycles,
                    offset=self.offset,
                    phase=self.phase)
    def __init__(self, amplitude:float, freq:float, n_cycles:float, offset:float, phase:float):
        self.amplitude = amplitude
        self.freq = freq
        self.n_cycles = n_cycles
        self.offset = offset
        self.phase = phase
    def get_time_array(self, sample_rate):
        return np.arange(0, self.n_cycles/self.freq, 1/sample_rate)
    def sample_wf(self, sample_rate):
        return self.amplitude * np.sin(2*np.pi*self.freq*self.get_time_array(sample_rate) - self.phase) + self.offset

class WF_Block_Constant(WF_Block_Base):
    '''A constant waveform for a specified duration.
    Cannot have children.'''
    def to_dict(self):
        return dict(_type=self.__class__.__name__, 
                    value=self.value,
                    duration=self.duration)
    def __init__(self, value:float, duration:float):
        self.value = value
        self.duration= duration
    def get_time_array(self, sample_rate):
        return np.arange(0, self.duration, 1/sample_rate)
    def sample_wf(self, sample_rate):
        return self.value * np.ones(len(self.get_time_array(sample_rate)))

class WF_Block_Arbitrary(WF_Block_Base):
    '''Block for holding arbitrary waveforms, more than just those predefined here.'''
    def to_dict(self):
        return dict(_type=self.__class__.__name__, 
                    values=self.values,
                    init_sample_rate=self.init_sample_rate)
    def __init__(self, values:np.ndarray, init_sample_rate:float):
        self.values = values
        self.init_sample_rate = init_sample_rate
    def get_time_array(self, sample_rate):
        return np.arange(0, len(self.values)/self.init_sample_rate, 1/sample_rate)
    def sample(self, sample_rate:float):
        if sample_rate == self.init_sample_rate:
            return self.values
        else:
            raise NotImplementedError('Interpolation of arbitrary waveforms not yet supported')

class WF_Block_Collection(WF_Block_Base):
    '''This is a special class. It represents a collection of other WF_Block_Base instances.'''
    def __init__(self, *blocks:WF_Block_Base):
        super().__init__()
        for block in blocks:
            self.add_child(child=block)
    def get_time_array(self, sample_rate:float):
        total_len = np.sum([len(block.get_time_array()) for block in self.blocks])
        return np.arange(0, total_len/sample_rate, 1/sample_rate)
    def sample(self, sample_rate:float):
        return np.concat( [block.sample_wf(sample_rate) for block in self.blocks] )
    def add_child(self, child:WF_Block_Base):
        assert isinstance(child, WF_Block_Base), f'Expected a child instance of WF_Block_Base, but got {type(child)}!'
        super(WF_Block_Base, self).add_child(child) # do not use WF_Block_Base's add_child method (which will just raise an error). Use State's.


if __name__ == '__main__':
    state = State()
    pund_tab = Tab('pund', 'PUND')
    state.add_child(pund_tab)
    state.add_child(Tab('ndpu', 'NDPU'))
    ch1_collection = WF_Block_Collection(WF_Block_PUND(1,1,1,1,1,False), WF_Block_Sine(1,1,1,1,1))
    ch2_collection = WF_Block_Collection()
    pund_tab.add_child(ch1_collection)
    pund_tab.add_child(ch2_collection)
    print(state.to_dict())

    d = {'_type': 'State', 'children': [{'name': 'PUND', 'id': 'pund', '_type': 'Tab', 'children': [{'_type': 'WF_Block_Collection', 'children': [{'_type': 'WF_Block_PUND', 'amplitude': 1, 'rise_time': 1, 'delay_time': 1, 'n_cycles': 1, 'offset': 1, 'ndpu': False}, {'_type': 'WF_Block_Sine', 'amplitude': 1, 'freq': 1, 'n_cycles': 1, 'offset': 1, 'phase': 1}]}, {'_type': 'WF_Block_Collection', 'children': []}]}, {'name': 'NDPU', 'id': 'ndpu', '_type': 'Tab', 'children': []}]}
    state = State.from_dict(d)
    print(state._children)
    print(state.to_dict())
