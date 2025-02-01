import numpy as np # only for typehinting


class _Base:
    py_id_counter = 0
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
        for cls in _Base._get_all_subclasses():
            if cls.__name__ == _type:
                this = cls(**d)
                return this
        else:
            raise ValueError(f'{_type} is not a valid subclass of _Base!')
    def to_dict(self)->dict:
        return dict(_type=self.__class__.__name__,
                    py_id=self.py_id)
    def __init__(self):
        self.parent = None
        self.py_id = _Base.py_id_counter
        _Base.py_id_counter += 1
    def update(self, **params):
        for k,e in params.items():
            setattr(self, k, float(e))
    def apply(self, func):
        func(self)
    def find_by_py_id(self, id):
        if self.py_id == id:
            return self
        else:
            return None    
    @property
    def selector(self)->str:
        return ''


class _BaseParent(_Base):
    @staticmethod
    def from_dict(d):
        children = d.pop('children', [])
        this = _Base.from_dict(d)
        for child in children:
            this.add_child( _BaseParent.from_dict(child) )
        return this
    def to_dict(self)->dict:
        res = super().to_dict()
        res.update( children=[child.to_dict() for child in self._children] )
        return res
    def __init__(self):
        super().__init__()
        self._children:list[_Base, _BaseParent] = []
    def apply(self, func):
        '''Apply func to every element in the tree lower than this element, including this element'''
        for child in self._children:
                child.apply(func)
        super().apply(func)
    def find_by_py_id(self, id):
        for child in self._children:
            if child.py_id == id:
                return child
            else:
                res = child.find_by_py_id(id)
                if res is not None:
                    return res
        return super().find_by_py_id(id)
    def add_child(self, child):
        assert any([isinstance(child, cls) for cls in _Base.__subclasses__()]), f'Child ({type(child)}) must be an instance of a subclass of _Base, e.g. {_Base.__subclasses__()}'
        self._children.append(child)
        child.parent = self
    def pop(self, idx:int):
        return self._children.pop(idx)
    def __getitem__(self, idx:int):
        assert isinstance(idx, int), f'List_WF_Block only supports integer indexing right now. No slicing.'
        return self._children[idx]
    def __setitem__(self, idx:int, child):
        assert isinstance(idx, int), f'List_WF_Block only supports integer indexing right now. No slicing.'
        # assert isinstance(child, AppState), f'Expected WF_Block_Base, but got {type(child)} which does not inherit from Abstrack_WF_Block!'
        self._children[idx] = child
    def swap_children(self, idx1:int, idx2:int):
        self[idx1], self[idx2] = self[idx2], self[idx1]


class TemplateWF(_Base):
    '''Abstract base class instructions.'''
    def get_skeleton(self)->tuple[np.ndarray, np.ndarray]:
        raise NotImplementedError
    def get_time_array(self, sample_rate:float)->np.ndarray:
        '''Get an array of times corresponding to this block, for the specified sample rate'''
        raise NotImplementedError
    def sample_wf(self, sample_rate:float)->np.ndarray:
        '''Get an array of values corresponding to this block, for the specified sample rate'''
        raise NotImplementedError
    def get_ROIs(self, sample_rate:float, offset:float=0, lblfmt:str='{prefix}.{suffix}')->dict[str,slice]:
        '''Get slices that correspond to ROIs of this waveform'''
        return {}
    @property
    def selector(self): # Here I am assuming that these elements are directly inside of the parent element
        i = self.parent._children.index(self)
        return (self.parent.selector if self.parent is not None else '') + f' [data-pyclassname]:nth-child({i+1})'

class _DeviceSettings(_BaseParent):
    def add_child(self, child):
        assert child.channel not in [child_.channel for child_ in self._children], f'A child representing this channel ({child.channel}) already exists!'
        return super().add_child(child)
    @property
    def selector(self):
        return (self.parent.selector + ' ' if self.parent is not None else '') + f'[data-pyclassname="{self.__class__.__name__}"]'


class AWGChannelSettings(_BaseParent):
    '''Base class for AWG settings, channel-specific settings'''
    def to_dict(self)->dict:
        res = super().to_dict()
        res.update(channel = self.channel, 
                   sample_rate = self.sample_rate)
        return res
    def __init__(self, channel:int, sample_rate:float=0):
        super().__init__()
        self._children:list[TemplateWF]
        self.channel = channel
        self.sample_rate = sample_rate
    def add_child(self, child):
        return super().add_child(child)
    @property
    def selector(self):
        return (self.parent.selector + ' ' if self.parent is not None else '') + f'[data-pyclassname="{self.__class__.__name__}"][data-channel="{self.channel}"]'
class AWGSettings(_DeviceSettings):
    '''Base class for AWG settings, non-channel-specific settings'''
    def to_dict(self)->dict:
        return super().to_dict()
    def __init__(self):
        super().__init__()
        self._children:AWGChannelSettings
    def add_child(self, child):
        assert isinstance(child, AWGChannelSettings), f'Expected child to be of type AWGChannelSettings, but got {type(child)}'
        return super().add_child(child)


class OscilloscopeChannelSettings(_Base):
    '''Base class for Oscilloscope settings, channel-specific settings'''
    def to_dict(self)->dict:
        res = super().to_dict()
        res.update( channel = self.channel,
                    vrange = self.vrange,
                    source = self.source,
                    transimpedance=self.transimpedance)
        return res
    def __init__(self, channel:int, vrange:float=1, source:str='No Source', transimpedance:float|None=None):
        super().__init__()
        self.channel = channel
        self.vrange = vrange
        self.source = source
        if 'tia' in source:
            self.transimpedance = transimpedance
        else:
            self.transimpedance = None
    @property
    def selector(self):
        return (self.parent.selector + ' ' if self.parent is not None else '') + f'[data-pyclassname="{self.__class__.__name__}"][data-channel="{self.channel}"]'
class OscilloscopeSettings(_DeviceSettings):
    '''Base class for Oscilloscope settings non-channel-specific settings'''
    def to_dict(self)->dict:
        res = super().to_dict()
        res.update(sample_rate = self.sample_rate,
                   trig_delay = self.trig_delay)
        return res
    def __init__(self, sample_rate:float=1, trig_delay:float=0):
        super().__init__()
        self._children:OscilloscopeChannelSettings
        self.sample_rate = sample_rate
        self.trig_delay = trig_delay
    def add_child(self, child):
        assert isinstance(child, OscilloscopeChannelSettings), f'Expected child to be of type OscilloscopeChannelSettings, but got {type(child)}'
        super().add_child(child)


class DUTSettings(_Base):
    def to_dict(self):
        res = super().to_dict()
        res.update(name = self.name,
                   area = self.area,
                   notes = self.notes)
    def __init__(self, name:str='', area:float=0, notes:str=''):
        super().__init__()
        self.name = name
        self.area = area
        self.notes = notes


class Tab(_BaseParent):
    '''This class represents Tabs in the app.'''
    def to_dict(self)->dict:
        res = dict(name=self.name, id=self.id)
        res.update( super().to_dict() )
        return res
    def __init__(self, id:str, name:str, **kwargs):
        super().__init__()
        self.id = id
        self.name = name
    def add_child(self, child):
        # Direct children of Tab should be _DeviceSettings, but only one of each type.
        assert child.__class__.__name__ not in [child_.__class__.__name__ for child_ in self._children], f'Tab already holds one of {child.__class__.__name__}!'
        assert isinstance(child, _DeviceSettings), f'Tab children should be any of: {_DeviceSettings._get_all_subclasses()}'
        return super().add_child(child)
    @property
    def selector(self):
        return (self.parent.selector if self.parent is not None else '') + f'#{self.id}' + ' '


class AppState(_BaseParent):
    '''This is the state of the app. Saves and loads from json. There should really only be one instance of AppState, but I won't enforce that.'''
    def __init__(self):
        super().__init__()
        self._children:list[Tab]
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
    def add_child(self, child):
        # Direct children of AppState should be Tab
        assert isinstance(child, Tab), f'Child is of type {type(child)}, but expected it to be of type Tab'
        return super().add_child(child)

    @property
    def selector(self):
        return '' if self.parent is None else self.parent.selector


base_class_dict = {cls.__name__:cls for cls in _Base._get_all_subclasses()}
