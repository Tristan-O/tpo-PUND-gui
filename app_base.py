class AppState:
    '''This is the state of the app. Saves and loads from json. There should really only be one instance of AppState, but I won't enforce that.'''
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
        for cls in AppState._get_all_subclasses():
            if cls.__name__ == _type:
                this = cls(**d)
                for child in children:
                    this.add_child( cls.from_dict(child) )
                return this
        else:
            raise ValueError(f'{_type} is not a valid subclass of AppState!')
    def to_dict(self)->dict:
        return dict(_type=self.__class__.__name__,
                    name=self.name,
                    children=[child.to_dict() for child in self._children])
    def __init__(self, name:str=''):
        self.name = name
        self._children:list[AppState] = []
    def add_child(self, child):
        assert any([isinstance(child, cls) for cls in AppState.__subclasses__()]), f'Child must be an instance of a direct subclass of AppState, e.g. {AppState.__subclasses__()}'
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


class DeviceSettings:
    '''Just a data storage class. Basically a dict with required inputs.'''
    def to_dict(self)->dict:
        return {k:e for k,e in self._params.items()}
    def __init__(self, **params):
        self._params = {k:e for k,e in params.items()}
    def update(self, **params):
        if any([k not in self._params for k in params.keys()]):
            raise ValueError('Cannot set a new parameter that was not initialized at start!')
        self._params.update(**params)


class Tab(AppState):
    '''This class represents Tabs in the app.'''
    def __init__(self, id:str, name:str, 
                 awg:DeviceSettings, 
                 oscilloscope:DeviceSettings,
                 tia:DeviceSettings, 
                 dut:DeviceSettings):
        super().__init__(name)
        self.id = id
        self.awg = awg
        self.oscilloscope = oscilloscope
        self.dut = dut
        self.tia = tia
    def to_dict(self)->dict:
        res = dict(name=self.name, id=self.id, awg=self.awg, 
                   oscilloscope=self.oscilloscope, dut=self.dut,
                   tia=self.tia)
        res.update( super().to_dict() )
        return res