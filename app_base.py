import numpy as np # only for typehinting


class _Base:
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
        return dict(_type=self.__class__.__name__)
    def __init__(self):
        pass


class _Parent(_Base):
    @staticmethod
    def from_dict(d):
        children = d.pop('children', [])
        this = _Base.from_dict(d)
        for child in children:
            this.add_child( _Parent.from_dict(child) )
        return this
    def to_dict(self)->dict:
        return dict(_type=self.__class__.__name__,
                    children=[child.to_dict() for child in self._children])
    def __init__(self):
        self._children:list[_Base, _Parent] = []
    def add_child(self, child):
        assert any([isinstance(child, cls) for cls in _Base.__subclasses__()]), f'Child must be an instance of a direct subclass of AppState, e.g. {_Base.__subclasses__()}'
        self._children.append(child)
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


class AWGChannelSettings(_Parent):
    '''Base class for AWG settings, channel-specific settings'''
    def to_dict(self)->dict:
        res = super().to_dict()
        res.update(channel = self.channel, 
                   sample_rate = self.sample_rate)
        return res
    def __init__(self, channel:int, sample_rate:float, template_wf:TemplateWF):
        super().__init__()
        self._children:list[TemplateWF]
        self.channel = channel
        self.sample_rate = sample_rate
        self.add_child( template_wf )
class AWGSettings(_Parent):
    '''Base class for AWG settings, non-channel-specific settings'''
    def to_dict(self)->dict:
        return super().to_dict()
    def __init__(self, channelsettings:list[AWGChannelSettings]):
        super().__init__()
        self._children:AWGChannelSettings
        for chan in channelsettings:
            self.add_child(chan)


class OscilloscopeChannelSettings(_Base):
    '''Base class for Oscilloscope settings, channel-specific settings'''
    def to_dict(self)->dict:
        res = super().to_dict()
        res.update( channel = self.channel,
                    vrange = self.vrange,
                    source = self.source)
        return res
    def __init__(self, channel:int, vrange:float, source:str):
        super().__init__()
        self.channel = channel
        self.vrange = vrange
        self.source = source
class OscilloscopeSettings(_Parent):
    '''Base class for Oscilloscope settings non-channel-specific settings'''
    def to_dict(self)->dict:
        res = super().to_dict()
        res.update(sample_rate = self.sample_rate,
                   duration = self.duration,
                   trig_delay = self.trig_delay)
        return res
    def __init__(self, channel_settings:list[OscilloscopeChannelSettings],
                 sample_rate:float, duration:float, trig_delay:float):
        super().__init__()
        self.sample_rate = sample_rate
        self.duration = duration
        self.trig_delay = trig_delay
        self._children:OscilloscopeChannelSettings
        for chan in channel_settings:
            self.add_child(chan)


class DUTSettings(_Base):
    def to_dict(self):
        res = super().to_dict()
        res.update(name = self.name,
                   area = self.area,
                   notes = self.notes)
    def __init__(self, name:str, area:float, notes:str=''):
        super().__init__()
        self.name = name
        self.area = area
        self.notes = notes


class Tab(_Parent):
    '''This class represents Tabs in the app.'''
    def to_dict(self)->dict:
        res = dict(name=self.name, id=self.id)
        res.update( super().to_dict() )
        return res
    def __init__(self, id:str, name:str, 
                 devices:list[AWGSettings,OscilloscopeSettings,DUTSettings]=[], **kwargs):
        super().__init__()
        self.id = id
        self.name = name
        for dev in devices:
            self.add_child(dev)


class AppState(_Parent):
    '''This is the state of the app. Saves and loads from json. There should really only be one instance of AppState, but I won't enforce that.'''
    def __init__(self):
        self._children:list[Tab]
        super().__init__()
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
