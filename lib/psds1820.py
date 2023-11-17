import machine, onewire, ds18x20
from time import sleep

ds_pin = machine.Pin(2) # CHANGE THIS
 
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

def get_temp():
	roms = ds_sensor.scan()
	if len(roms) == 0:
		return None
	ds_sensor.convert_temp()
	try:
		temp = ds_sensor.read_temp(roms[0])
		return float('{0:.2f}'.format(temp))
	except:
		return None

# while True:
#     print(get_temp())
#     sleep(1)