from machine import Pin, I2C, ADC, PWM
# from ssd1306 import SSD1306_I2C
from sh1106 import SH1106_I2C as SSD1306_I2C
import framebuf,sys
import time

btnLeft = Pin(0, Pin.IN, Pin.PULL_DOWN)
btnOK = Pin(1, Pin.IN, Pin.PULL_DOWN)
btnRight = Pin(3, Pin.IN, Pin.PULL_DOWN)
btnBack = Pin(7, Pin.IN, Pin.PULL_DOWN)
ledRed = Pin(4, Pin.OUT)
ledYellow = Pin(5, Pin.OUT)
ledGreen = Pin(6, Pin.OUT)

display_width = 128 # SSD1306 width
display_height = 64   # SSD1306 height
TEST_DELAY = 0.5

screen_i2c = I2C(1,scl=Pin(19),sda=Pin(18))

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
oled.fill(0)
oled.text("Taster", 0, 0, 1)
oled.text("Press BACK", 0, 10, 1)
oled.show()
while True:
	if btnBack.value() == 1:
		break
oled.fill(0)
oled.show()
