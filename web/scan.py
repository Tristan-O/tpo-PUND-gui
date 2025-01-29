import pyvisa
from waveform import DeviceSettings

# Create a Resource Manager
rm = pyvisa.ResourceManager()

# List all available resources
resources = rm.list_resources()
print(resources)
resources = ('TCPIP0::10.97.108.205::INSTR','TCPIP0::10.97.108.206::INSTR',)

# Print the available resources and additional information
if resources:
    print("Available connections and device information:")
    for resource in resources:
        print(f"Resource: {resource}")
        try:
            instrument = rm.open_resource(resource)
            print(f"  Manufacturer: {instrument.query('*IDN?')}")
            instrument.close()
        except Exception as e:
            print(f"  Could not retrieve information: {e}")
else:
    print("No available connections found.")

class Rigol_DG2102_Settings(DeviceSettings):
    '''Rigol AWG settings'''
    def __init__(self, ch1_sample_rate, ch2_sample_rate):
        super().__init__(ch1_sample_rate=ch1_sample_rate,
                         ch2_sample_rate=ch2_sample_rate)

class Rigol_DG2102(DeviceSettings):
    def __init__(self):
        pass

class Rigol_DHO1074_Settings(DeviceSettings):
    '''Rigol oscilloscope settings. The sample_rate is actually calculated, not set.'''
    memory_depth = {0:None, 1:50e6, 2:25e6, 3:10e6, 4:25e6}
    def __init__(self, ch1_range, ch2_range, ch3_range, ch4_range, total_time):
        super().__init__(ch1_range=ch1_range,
                        ch2_range=ch2_range,
                        ch3_range=ch3_range,
                        ch4_range=ch4_range,
                        total_time=total_time,
                        calculated_sample_rate=None)
    @property
    def max_memory_depth(self):
        n_chan_in_use = 0
        for i in range(4):
            n_chan_in_use += int(self.params[f'ch{i}_range'] != 0)
        return Rigol_DHO1074_Settings.memory_depth[ n_chan_in_use ]

    def calculate_sample_rate(self, time:float):
        self.params['calculated_sample_rate'] = self.max_memory_depth/time
        return self.params['calculated_sample_rate']
    def update(self, **params):
        temp = self.max_memory_depth
        super().update(**params)
        if self.max_memory_depth != temp:
            self.params['calculated_sample_rate'] = None


class DUT:
    def __init__(self, area:float, name:str, notes:str=''):
        self.area = area
        self.name = name
        self.notes = notes