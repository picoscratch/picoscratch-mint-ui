from machine import Pin, I2C, ADC, PWM
from ssd1306 import SSD1306_I2C
import framebuf,sys
import time
from psds1820 import get_temp
import dftds # TDS/ppm library

btnLeft = Pin(0, Pin.IN, Pin.PULL_DOWN)
btnOK = Pin(1, Pin.IN, Pin.PULL_DOWN)
btnRight = Pin(3, Pin.IN, Pin.PULL_DOWN)
ledRed = Pin(4, Pin.OUT)
ledYellow = Pin(5, Pin.OUT)
ledGreen = Pin(6, Pin.OUT)

display_width = 128 # SSD1306 width
display_height = 64   # SSD1306 height
TEST_DELAY = 0.5

screen_i2c = I2C(1,scl=Pin(27),sda=Pin(26))

oled = SSD1306_I2C(display_width, display_height, screen_i2c)

oled.fill(1)
oled.show()

time.sleep(TEST_DELAY)
oled.fill(0)
oled.show()

time.sleep(TEST_DELAY)
oled.fill(0)
oled.text("LED Rot", 0, 0, 1)
ledRed.on()
oled.show()

time.sleep(TEST_DELAY)
oled.text("LED Gelb", 0, 10, 1)
ledYellow.on()
oled.show()

time.sleep(TEST_DELAY)
oled.text("LED Gruen", 0, 20, 1)
ledGreen.on()
oled.show()

time.sleep(TEST_DELAY)
ledRed.off()
ledYellow.off()
ledGreen.off()

oled.fill(0)
oled.text("Taster", 0, 0, 1)
oled.text("Press UP", 0, 10, 1)
oled.show()
while True:
	if btnLeft.value() == 1:
		break
oled.fill(0)
oled.text("Taster", 0, 0, 1)
oled.text("Press DOWN", 0, 10, 1)
oled.show()
while True:
	if btnRight.value() == 1:
		break
oled.fill(0)
oled.text("Taster", 0, 0, 1)
oled.text("Press OK", 0, 10, 1)
oled.show()
while True:
	if btnOK.value() == 1:
		break

for i in range(0, 5):
	oled.fill(0)
	oled.text("Temperatur", 0, 0, 1)
	oled.text(str(get_temp()), 0, 10, 1)
	oled.show()
	time.sleep(TEST_DELAY)

def get_tds():
	try:
		tds_sensor = dftds.GravityTDS(28, adc_range=65535, k_value_repository=dftds.KValueRepositoryFlash("tds_calibration.json"))
		tds_sensor.begin()
		temp = get_temp()
		if temp == None:
			# tds_sensor.temperature = 25
			return None
		# else:
		tds_sensor.temperature = temp
		# tds_sensor.temperature = get_temp() # type: ignore
		tds_value = tds_sensor.update()
		return float('{0:.2g}'.format(tds_value))
	except:
		return None

for i in range(0, 5):
	oled.fill(0)
	oled.text("TDS", 0, 0, 1)
	oled.text(str(get_tds()), 0, 10, 1)
	oled.show()
	time.sleep(TEST_DELAY)

oled.fill(0)
oled.show()