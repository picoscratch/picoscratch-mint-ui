from machine import Pin, I2C, ADC, PWM
from ssd1306 import SSD1306_I2C
import framebuf,sys
import time

dw = 128 # SSD1306 width
dh = 64   # SSD1306 height
scri2c = I2C(1,scl=Pin(27),sda=Pin(26))

disp = SSD1306_I2C(dw, dh, scri2c)

disp.fill(1)
disp.show()

time.sleep(1)
disp.fill(0)
disp.show()
