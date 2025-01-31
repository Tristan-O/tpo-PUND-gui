import numpy as np
from app_base import TemplateWF, _Parent


class CollectionTemplateWF(_Parent, TemplateWF):
    '''This is a special class. It represents a collection of other TemplateWF instances.
    The multiple inheritance here pulls from _Parent first if it can, then TemplateWF'''
    def __init__(self, *blocks:TemplateWF):
        super().__init__()
        self._children:list[TemplateWF]
        for block in blocks:
            self.add_child(child=block)
    def get_skeleton(self):
        t = [0]
        v = []
        for i,block in enumerate(self._children):
            t_,v_ = block.get_skeleton()
            if i>0: # exclude first point for subsequent blocks
                t_ = t_[1:]
                v_ = v_[1:]
            t.extend( (t_+t[-1]).tolist() )
            v.extend( v_.tolist() )
        return np.array(t[1:]), np.array(v)
    def get_time_array(self, sample_rate:float):
        total_len = np.sum([len(block.get_time_array()) for block in self.blocks])
        return np.arange(0, total_len/sample_rate, 1/sample_rate)
    def sample(self, sample_rate:float):
        return np.concat( [block.sample_wf(sample_rate) for block in self.blocks] )
    def add_child(self, child:TemplateWF):
        assert isinstance(child, TemplateWF), f'Expected a child instance of TemplateWF, but got {type(child)}!'
        super().add_child(child)
    def get_ROIs(self, sample_rate:float, offset:float=0, lblfmt:str='{prefix}.{childIdx}.{suffix}')->dict[str,slice]:
        d = dict()
        for i,block in enumerate(self._children):
            d.update(block.get_ROIs(sample_rate, offset, lblfmt.format(childIdx=i)))
            offset += block.get_time_array()[-1]
        return d


class PUNDTemplateWF(TemplateWF):
    '''A PUND waveform. Equivalent to making the amplitude negative.
    Cannot have children.'''
    _selector = 'pund'
    def to_dict(self):
        return dict(_type=self.__class__.__name__,
                    amplitude=self.amplitude, 
                    rise_time=self.rise_time, 
                    delay_time=self.delay_time, 
                    n_cycles=self.n_cycles, 
                    offset=self.offset)
    def __init__(self, amplitude:float=1.0, rise_time:float=350e-6, delay_time:float=350e-6, n_cycles:float=4., offset:float=0.):
        super().__init__()
        self.amplitude = amplitude
        self.rise_time = rise_time
        self.delay_time = delay_time
        self.n_cycles = n_cycles
        self.offset = offset
    def get_skeleton(self):
        t = [0]
        v = [self.offset]
        for n in np.arange(4*self.n_cycles+1):
            for t_ in (self.rise_time, self.rise_time, self.delay_time):
                t.append(t_+t[-1])
            v.extend( [self.offset+self.amplitude*(-1 if n%4>1 else 1), self.offset, self.offset] )
        for t_ in t[::-1]:
            if t_ > self.n_cycles*(4*self.delay_time + 8*self.rise_time):
                t.pop(-1)
                v.pop(-1)
            else:
                break
        return np.array(t),np.array(v)
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
        return self.offset + self.amplitude*pund(time, self.rise_time, self.delay_time)
    def get_ROIs(self, sample_rate:float, offset:float=0, lblfmt:str='{prefix}.{suffix}')->dict[str,slice]:
        d = dict()
        T = 4*self.delay_time + 8*self.rise_time # wf period
        length = self.n_cycles*T/sample_rate # array length at this sampling rate
        pulse_len = 2*self.rise_time/sample_rate # array length of a pulse
        start = offset/sample_rate # starting idx

        if self.amplitude > 0: # if labels will be drawn from PUND or NDPU string
            pre = 'PUND'
        elif self.amplitude < 0:
            pre = 'NDPU'
        else:
            return d # no labels for a flat wf

        for n in np.arange(self.n_cycles):
            for p in range(4):
                stop  = start + pulse_len # stopping idx
                if stop > length:
                    break
                d[lblfmt.format(prefix=pre[p], suffix=int(n))] = slice(int(start), int(stop))
                start += (2*self.rise_time + self.delay_time)/sample_rate
        return d


class SineTemplateWF(TemplateWF):
    '''A sine waveform.
    Cannot have children.'''
    def to_dict(self):
        return dict(_type=self.__class__.__name__,
                    amplitude=self.amplitude,
                    freq=self.freq,
                    n_cycles=self.n_cycles,
                    offset=self.offset,
                    phase=self.phase)
    def __init__(self, amplitude:float=1.0, freq:float=1000, n_cycles:float=4., offset:float=0., phase:float=0.):
        super().__init__()
        self.amplitude = amplitude
        self.freq = freq
        self.n_cycles = n_cycles
        self.offset = offset
        self.phase = phase
    def get_skeleton(self):
        sample_rate = self.freq*50 # be well above nyquist. 50 datapoints per cycle.
        return self.get_time_array(sample_rate), self.sample_wf(sample_rate)
    def get_time_array(self, sample_rate):
        return np.arange(0, self.n_cycles/self.freq+1/sample_rate, 1/sample_rate)
    def sample_wf(self, sample_rate):
        return self.amplitude * np.sin(2*np.pi*self.freq*self.get_time_array(sample_rate) - self.phase) + self.offset


class ConstantTemplateWF(TemplateWF):
    '''A constant waveform for a specified duration.
    Cannot have children.'''
    def to_dict(self):
        return dict(_type=self.__class__.__name__,
                    value=self.value,
                    duration=self.duration)
    def __init__(self, value:float=0, duration:float=1e-3):
        super().__init__()
        self.value = value
        self.duration= duration
    def get_skeleton(self):
        return np.array([0, self.duration]), np.array([self.value]*2)
    def get_time_array(self, sample_rate):
        return np.arange(0, self.duration, 1/sample_rate)
    def sample_wf(self, sample_rate):
        return self.value * np.ones(len(self.get_time_array(sample_rate)))


class ArbitraryTemplateWF(TemplateWF):
    '''Block for holding arbitrary waveforms, more than just those predefined here.'''
    def to_dict(self):
        return dict(_type=self.__class__.__name__,
                    values=self.values,
                    init_sample_rate=self.init_sample_rate)
    def __init__(self, values:np.ndarray=[], init_sample_rate:float=1):
        super().__init__()
        self.values = np.array(values)
        self.init_sample_rate = init_sample_rate
    def get_skeleton(self):
        return self.get_time_array(self.init_sample_rate), self.sample_wf(self.init_sample_rate)
    def get_time_array(self, sample_rate):
        return np.arange(0, len(self.values)/self.init_sample_rate, 1/sample_rate)
    def sample_wf(self, sample_rate:float):
        if sample_rate == self.init_sample_rate:
            return self.values
        else:
            raise NotImplementedError('Interpolation of arbitrary waveforms not yet supported')



# TODO
class TriangleTemplateWF(TemplateWF):
    pass
class SquareTemplateWF(TemplateWF):
    pass


wf_class_dict = {cls.__name__:cls for cls in TemplateWF._get_all_subclasses()} # used for creating new waveform blocks
