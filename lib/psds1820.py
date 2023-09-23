import machine, onewire, ds18x20
from time import sleep

ds_pin = machine.Pin(2) # CHANGE THIS
 
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

roms = ds_sensor.scan()

def get_temp():
    ds_sensor.convert_temp()
    return ds_sensor.read_temp(roms[0])

# while True:
#     print(get_temp())
#     sleep(1)