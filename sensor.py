import dftds # TDS sensor
from machine import Pin, ADC, I2C
from psds1820 import get_temp
from mh_z19 import MH_Z19
import psscd4x

i2c = I2C(0, sda=Pin(8), scl=Pin(9))

def get_tds():
	try:
		if not Pin(10, Pin.IN).value():
			return None
		tds_sensor = dftds.GravityTDS(28, adc_range=65535, k_value_repository=dftds.KValueRepositoryFlash("tds_calibration.json"))
		tds_sensor.begin()
		temp = get_temp()
		if temp == None:
			tds_sensor.temperature = 25
			#return None
		else:
			tds_sensor.temperature = temp
		# tds_sensor.temperature = get_temp()
		tds_value = tds_sensor.update()
		return float('{0:.2g}'.format(tds_value))
	except:
		return None

def read_ph():
	m = 11.48
	n = -11.1553
	vcor = 1.38
	# Create an ADC object linked to pin 36
	adc = ADC(Pin(27, Pin.IN))
	volt = adc.read_u16()
	volt = volt * (3.3 / 65536) * vcor
	ph = m*volt+n
	if ph > 14:
		return None
	return float('{0:.2g}'.format(ph))


def read_co2():
	sensor = MH_Z19(Pin(8), Pin(9), 1)
	return sensor.read_co2()

def get_temp_0():
	return get_temp(0)

sensors = {
	"temp": {
		"read": get_temp_0,
		"unit": "*C",
		"min": -10,
		"max": 40,
		"friendlyName": "Temp.",
		"toolow": 10,
		"good": 20,
		"warn": 30,
		"bad": 40
	},
	"tds": {
		"read": get_tds,
		"unit": "ppm",
		"min": 0,
		"max": 500,
		"friendlyName": "TDS",
		"toolow": 70,
		"good": 80,
		"warn": 200,
		"bad": 400
	},
	#"co2": {
	#	"read": read_co2,
	#	"unit": "ppm",
	#	"min": 300, ######################## TODO: change these values to sth better
	#	"max": 2200,
	#	"friendlyName": "CO2",
	#	"toolow": 0,
	#	"good": 400,
	#	"warn": 1300,
	#	"bad": 1700
	#},
	"co2": {
		"isI2C": True,
		"addr": psscd4x.I2C_ADDR,
		"read": psscd4x.read_i2c_co2,
		"init": psscd4x.driver_init,
		"unit": "ppm",
		"min": 100,
		"max": 2000,
		"friendlyName": "CO2",
		"toolow": -1,
		"good": 800,
		"bad": 1200
	},
	"ph": {
		"read": read_ph,
		"unit": "pH",
		"min": 0,
		"max": 14,
		"friendlyName": "pH",
		"toolow": -1,
		"good": 800,
		"bad": 1200,
	}
}

def max4466():
	analog_value = ADC(28)
	conversion_factor =3.3/(65536)
	reading = analog_value.read_u16()*conversion_factor
	return reading

lastI2Cids = []

def read_i2c_sensors():
	global lastI2Cids
	resultlist = []

	i2c_ids = i2c.scan()
	for sensorID in sensors:
		sensor = sensors[sensorID]
		if not "isI2C" in sensor:
			continue # If the sensor is not an I2C sensor, skip it
		if not sensor["addr"] in i2c_ids:
			continue # If the sensor's address is not in the scan result, skip it
		if not sensor["addr"] in lastI2Cids:
			sensor["init"](i2c) # If this is the first time we see this sensor, initialize it
		
		result = {
			"unit": sensor["unit"],
			"min": sensor["min"],
			"max": sensor["max"],
			"friendlyName": sensor["friendlyName"],
			"isI2C": True,
			"isLoading": False,
			"value": None,
			"traffic": {
				"good": sensor["good"],
				"bad": sensor["bad"]
			},
			"id": sensorID
		}
		value = sensor["read"]() # Read the sensor
		if value == None:
			result["isLoading"] = True # Sensor is still initializing
		else:
			result["value"] = value
		
		resultlist.append(result)
	
	lastI2Cids = i2c_ids
	return resultlist

def read_legacy_sensors():
	resultlist = []
	for sensorID in sensors:
		sensor = sensors[sensorID]
		if "isI2C" in sensor:
			continue # If the sensor is an I2C sensor, skip it
		
		result = {
			"unit": sensor["unit"],
			"min": sensor["min"],
			"max": sensor["max"],
			"friendlyName": sensor["friendlyName"],
			"isI2C": False,
			"isLoading": False,
			"value": None,
			"traffic": {
				"good": sensor["good"],
				"bad": sensor["bad"]
			},
			"id": sensorID
		}
		value = sensor["read"]() # Read the sensor
		if value == None:
			result["isLoading"] = True # Sensor is still initializing
		else:
			result["value"] = value
		
		resultlist.append(result)
	return resultlist

def read_sensors():
	return read_i2c_sensors() + read_legacy_sensors()