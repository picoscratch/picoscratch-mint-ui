from machine import Pin
import time

BTN_WAIT = 0.1

class Button:
	pin: Pin
	pressed = False

	def __init__(self, pin: Pin):
		self.pin = pin
		#self.pin.irq(trigger=Pin.IRQ_RISING, handler=self._on_press)
	
	def _on_press(self, pin):
		print("Press")
		self.pressed = True

	def value(self):
		#pressed = self.pressed
		##print("V" + str(pressed))
		#self.pressed = False
		#return pressed
		return self.pin.value()
	
	def wait(self):
		while True:
			v = self.value()
			if v:
				break
			time.sleep(BTN_WAIT)

def waitForAnyButton(*args):
	while True:
		for i, b in enumerate(args):
			v = b.value()
			if v:
				return i
		time.sleep(BTN_WAIT)

if __name__ == "__main__":
	btnUp = Button(Pin(0, Pin.IN, Pin.PULL_DOWN))
	btnOK = Button(Pin(1, Pin.IN, Pin.PULL_DOWN))
	btnDown = Button(Pin(3, Pin.IN, Pin.PULL_DOWN))
	
	print(waitForAnyButton(btnUp, btnOK, btnDown))
