from machine import unique_id

def get_serial():
	uid = unique_id()
	serial_number = ''.join(['{:02X}'.format(byte) for byte in uid])
	return serial_number