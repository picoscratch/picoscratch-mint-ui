import scd4x

I2C_ADDR = 0x62
scd = None

def driver_init(i2c):
	global scd
	scd = scd4x.SCD4X(i2c)
	scd.start_periodic_measurement()

def read_i2c_co2():
	return scd.CO2