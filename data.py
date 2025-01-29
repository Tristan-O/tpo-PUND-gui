import numpy as np
from templatewf import WF_Block_Collection, WF_Block_PUND, WF_Block_Sine


class Data:
    def _calculate_data_shift(self)->int:
        '''Use cross correlation to the template waveform to determine if data is shifted'''
        ideal = self._template.sample_wf(self.sample_rate)
        raise NotImplementedError
        
    def __init__(self, data:np.ndarray, sample_rate:float, template:WF_Block_Collection|None=None):
        self._data = data
        self.sample_rate = sample_rate
        self._template = template
        self.binning = 1
        
        if self._template is not None:
            self.shift = self._calculate_data_shift()
        else:
            self.shift = 0

class DataPair:
    pass