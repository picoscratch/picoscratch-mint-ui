from machine import Pin, I2C
#from ssd1306 import SSD1306_I2C
from sh1106 import SH1106_I2C as SSD1306_I2C
import framebuf

display_width = 128 # SSD1306 width
display_height = 64   # SSD1306 height
# picoscratch_logo = bytearray(b'BM>\x02\x00\x00\x00\x00\x00\x00>\x00\x00\x00(\x00\x00\x00@\x00\x00\x00@\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x02\x00\x00\xc4\x0e\x00\x00\xc4\x0e\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xff\xfc\x00\x00\x00\x00\x00\x0f\xff\xff\x80\x00\x00\x00\x00\x1f\xff\xff\xe0\x00\x00\x00\x00?\x00\x0f\xf0\x00\x00\x00\x00|\x00\x01\xf8\x00\x00\x00\x00x\x00\x00|\x00\x00\x00\x00\xf0\x00\x00>\x00\x00\x00\x00\xe0\x00\x00\x1e\x00\x00\x00\x00\xe0\xff\xf8\x0e\x00\x00\x00\x00\xe0\x0c\x0e\x0f\x00\x00\x00\x00\xe0\x0c\x03\x0f\x00\x00\x00\x00\xf0\x0c\x03\x07\x00\x00\x00\x00x\x04\x01\x07\x00\x00\x00\x00|\x04\x01\x07\x00\x00\x00\x00?\x04\x02\x0f\x00\x00\x00\x00\x1f\x04\x06\x0f\x00\x00\x00\x00\x0f\x04x\x1e\x00\x00\x00\x00\x07\x07\x80\x1e\x00\x00\x00\x00\x07\x04\x00<\x00\x00\x00\x00\x07\x04\x00|\x00\x00\x00\x00\x07\x04\x01\xf8\x00\x00\x00\x00\x07\x04\x0f\xf0\x00\x00\x00\x00\x0f\x04\x1f\xe0\x00\x00\x00\x00\x1f\x04\x1f\xc0\x00\x00\x00\x00?\x04\x03\xe0\x00\x00\x00\x00|\x04\x01\xe0\x00\x00\x00\x00x\x04\x00\xe0\x00\x00\x00\x00p\x04\x00\xe0\x00\x00\x00\x00\xf0\x07\xf0\xe0\x00\x00\x00\x00\xf0\xff\xe0\xe0\x00\x00\x00\x00\xf0\x00\x00\xe0\x00\x00\x00\x00\xf0\x00\x01\xe0\x00\x00\x00\x00x\x00\x03\xe0\x00\x00\x00\x00x\x00\x07\xc0\x00\x00\x00\x00>\x07\xff\xc0\x00\x00\x00\x00\x1f\xff\xff\x80\x00\x00\x00\x00\x0f\xff\xfe\x00\x00\x00\x00\x00\x03\xff\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
lineskip = 15

# 0x3C i2c address usually, can also rarely be 0x3D
screen_i2c = I2C(1,scl=Pin(27),sda=Pin(26))  # start I2C on I2C1 (GPIO 26/27)
# i2c_addr = [hex(ii) for ii in screen_i2c.scan()] # get I2C address in hex format
# if i2c_addr==[]:
# 	print('No I2C Display Found') 
# 	sys.exit() # exit routine if no dev found
# else:
# 	print("I2C Address      : {}".format(i2c_addr[0])) # I2C device address
# 	print("I2C Configuration: {}".format(screen_i2c)) # print I2C params

oled = SSD1306_I2C(display_width, display_height, screen_i2c) # oled controller

def invertArea(oled, x, y, w, h):
	for i in range(w):
		for j in range(h):
			oled.pixel(x+i, y+j, not oled.pixel(x+i, y+j))

def readPBM(filename):
	with open(filename, "rb") as f:
		f.readline() # Magic number
		f.readline() # Creator comment
		dim = f.readline() # Dimensions
		data = bytearray(f.read())
	w, h = dim.split()
	print("PBM " + str(filename) + ": " + str(int(w)) + "x" + str(int(h)) + " " + str(len(data)) + " bytes")
	fb = framebuf.FrameBuffer(data, int(w), int(h), framebuf.MONO_HLSB)
	invertArea(fb, 0, 0, int(w), int(h))
	return fb

def drawLogo(logo, txt_array):
	# fb = framebuf.FrameBuffer(logo, 64, 64, framebuf.MONO_HLSB)

	oled.fill(0)
	oled.blit(logo, 0, 10)

	start_x = 40
	start_y = 12
	for iter_ii,txt in enumerate(txt_array):
		oled.text(txt, start_x, start_y+(iter_ii*lineskip))
	
	oled.show()