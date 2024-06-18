import serial
import codecs
from datetime import datetime

LogFolder = '/home/kosh/Documents/'
Port = serial.Serial(port = '/dev/ttyUSB0', baudrate = 115200)

# Словарь с параметрами.
TCU = {}
Begin = 0
DataArray = []

# Логирование
def to_log(Init = 0):
	Date = datetime.now().strftime("%Y-%m-%d")
	LogFile = LogFolder + 'AT_log_' + Date + '.log'

	if Init == 1:
		File = codecs.open(LogFile, 'w', 'utf8')
		Text = 'Date\tTime\t'
		for Key in TCU.keys():
			Text += Key + '\t'
		
		File.write(Text + '\n')
		File.close()
		return

	Date = datetime.now().strftime("%d.%m.%Y")
	Time = datetime.now().strftime("%H:%M:%S")
	Time += datetime.now().strftime(".%f")[:4]
	Text = Date + '\t' + Time + '\t'
	for Key in TCU.keys():
		Text += str(TCU[Key]) + '\t'
		
	File = codecs.open(LogFile, 'a', 'utf8')
	File.write(Text + '\n')
	File.close()

def data_update():
	global TCU
	global DataArray
	
	TCU['DrumRPM'] = get_uint(0)
	TCU['OutputRPM'] = get_uint(2)
	TCU['CarSpeed'] = get_byte(4)
	TCU['SpdTimerVal'] = get_uint(5)
	TCU['OilTemp'] = get_int(7)
	TCU['TPS'] = get_uint(9)
	TCU['SLT'] = get_byte(11)
	TCU['SLN'] = get_byte(12)
	TCU['SLU'] = get_byte(13)
	TCU['S1'] = get_byte(14)
	TCU['S2'] = get_byte(15)
	TCU['S3'] = get_byte(16)
	TCU['S4'] = get_byte(17)
	TCU['Selector'] = get_byte(18)
	TCU['ATMode'] = get_byte(19)
	TCU['Gear'] = get_byte(20)
	TCU['GearChange'] = get_byte(21)
	TCU['Break'] = get_byte(22)
	TCU['EngineWork'] = get_byte(23)
	TCU['SlipDetected'] = get_byte(24)
	to_log()

def get_byte(N):
	return int.from_bytes(DataArray[N] + b'\x00', byteorder = 'little', signed = False)
def get_int(N):
	return int.from_bytes(DataArray[N] + DataArray[N + 1], byteorder = 'little', signed = True)
def get_uint(N):
	return int.from_bytes(DataArray[N] + DataArray[N + 1], byteorder = 'little', signed = False)

def read_port():
	global Begin
	global DataArray
	
	Byte = Port.read()
	#print(Byte)
	if Begin == 0:
		if Byte == b'\x40':
			DataArray.clear()
			Begin = 1
	elif Begin == 1:
		Replace = 0 
		if Byte == b'\x0a':
			Byte = Port.read()
			Replace = 1
			if Byte == b'\x82':
				Byte = b'\x40'
			if Byte == b'\x83':
				Byte = b'\x0d'
			if Byte == b'\x84':
				Byte = b'\x0a'
		if Replace == 0 and Byte == b'\x0d':
			data_update()
			Begin = 0
		else:
			DataArray.append(Byte)

def tcu_init():
	TCU['DrumRPM'] = 0
	TCU['OutputRPM'] = 0
	TCU['CarSpeed'] = 0
	TCU['SpdTimerVal'] = 0
	TCU['OilTemp'] = 0
	TCU['TPS'] = 0
	TCU['SLT'] = 0
	TCU['SLN'] = 0
	TCU['SLU'] = 0
	TCU['S1'] = 0
	TCU['S2'] = 0
	TCU['S3'] = 0
	TCU['S4'] = 0
	TCU['Selector'] = 0
	TCU['ATMode'] = 0
	TCU['Gear'] = 0
	TCU['GearChange'] = 0
	TCU['Break'] = 0
	TCU['EngineWork'] = 0
	TCU['SlipDetected'] = 0

tcu_init()
to_log(1)
while 1:
	read_port()