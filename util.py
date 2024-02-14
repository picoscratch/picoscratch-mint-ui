from machine import unique_id, Pin

def get_serial():
	uid = unique_id()
	serial_number = ''.join(['{:02X}'.format(byte) for byte in uid])
	return serial_number

def powerSave(value=None):
	pin = Pin("WL_GPIO1")
	if value == None:
		if pin.value():
			return False
		else:
			return True
	else:
		if value:
			pin.value(0)
		else:
			pin.value(1)