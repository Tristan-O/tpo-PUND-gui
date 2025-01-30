import pyvisa
from app_base import DeviceSettings

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

