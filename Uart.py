import serial
import os
import threading
from datetime import datetime
import time
import serial.tools.list_ports
import codecs

TpsGridSize = 21
TempGridSize = 31
DeltaRPMGridSize = 21

Parameters = (	  ('uint16_t', 'EngineRPM')
				, ('uint16_t', 'DrumRPM')
				, ('int16_t', 'DrumRPMDelta')
				, ('uint16_t', 'OutputRPM')
				, ('uint8_t', 'CarSpeed')
				, ('int16_t', 'OilTemp')
				, ('uint16_t', 'TPS')
				, ('uint16_t', 'InstTPS')
				, ('uint16_t', 'SLT')
				, ('uint16_t', 'SLN')
				, ('uint16_t', 'SLU')
				, ('uint8_t', 'S1')
				, ('uint8_t', 'S2')
				, ('uint8_t', 'S3')
				, ('uint8_t', 'S4')
				, ('uint8_t', 'Selector')
				, ('uint8_t', 'ATMode')
				, ('int8_t', 'Gear')
				, ('int8_t', 'GearChange')
				, ('uint8_t', 'GearStep')
				, ('uint8_t', 'LastStep')
				, ('uint8_t', 'Gear2State')
				, ('uint8_t', 'Break')
				, ('uint8_t', 'EngineWork')
				, ('uint8_t', 'SlipDetected')
				, ('uint8_t', 'Glock')
				, ('uint8_t', 'GearUpSpeed')
				, ('uint8_t', 'GearDownSpeed')
				, ('uint8_t', 'GearChangeTPS')
				, ('uint16_t', 'GearChangeSLT')
				, ('uint16_t', 'GearChangeSLN')
				, ('uint16_t', 'GearChangeSLU')
				, ('uint16_t', 'LastPDRTime')
				, ('uint16_t', 'CycleTime_x10')
				, ('uint8_t', 'DebugMode')
				, ('uint16_t', 'RawTPS')
				, ('uint16_t', 'RawOIL')
				)

Tables = (	  ('SLTGraph', 						'uint16_t',		TpsGridSize)
			, ('SLTTempCorrGraph', 				'int16_t',		TempGridSize)
			, ('SLNGraph', 						'uint16_t', 	TpsGridSize)
			, ('SLUGear2Graph', 				'uint16_t', 	TpsGridSize)
			, ('SLUGear2TempCorrGraph',			'int16_t', 		TempGridSize)
			, ('SLUGear2TPSAdaptGraph', 		'int16_t', 		TpsGridSize)						
			, ('SLUGear2TempAdaptGraph',		'int16_t', 		TempGridSize)
			, ('Gear2AdvGraph', 				'int16_t',		DeltaRPMGridSize)			
			, ('Gear2AdvAdaptGraph', 			'int16_t',		DeltaRPMGridSize)			
			, ('SLUGear3Graph', 				'uint16_t', 	TpsGridSize)
			, ('SLUGear3DelayGraph', 			'uint16_t',		TpsGridSize)
			, ('SLUG3DelayTempCorrGraph',		'int16_t',		TempGridSize)
			, ('SLUGear3TPSAdaptGraph',			'int16_t',		TpsGridSize)
			, ('SLUGear3TempAdaptGraph',		'int16_t',		TempGridSize)
			, ('SLNGear3Graph', 				'uint16_t',		TpsGridSize)
			, ('SLNGear3OffsetGraph', 			'int16_t',		TpsGridSize)
			, ('TPSGraph', 						'int16_t',		TpsGridSize)
			, ('OilTempGraph', 					'int16_t',		TempGridSize)
			)

# Прием данных по UART
class _uart:
	def __init__(self, Folder, Baudrate):
		self.TCU = {}				# Словарь с параметрами.
		self.TableData = []			# Буфер для таблицы.
		self.Begin = 0				# Флаг начала пакета.
		self.DataArray = []			# Массив байт.
		self.LogFolder = Folder		# Папка с логами.
		self.LogFile = ''
		
		self.Serial = serial.Serial()			# Порт.
		self.Serial.baudrate = Baudrate			# Скорость.
		
		if not os.path.isdir(self.LogFolder):	# Проверка наличия папки.
			os.mkdir(self.LogFolder)

		self.WriteLog = 1		# Флаг записи лога.
		# Переменные для выделения куска лога по кнопке.
		self.LogBuffer = []		# Кольцевой буфер лога.
		self.LogCounter = 0		# Счетчик для строк буфера.
		self.LogNumber = 0		# Номер куска.
		
		self.PortReading = 0
		self.SerialRead = threading.Thread(target = self.read_port, daemon = True).start()
		
		self.NewData = 1			# Флаг, получен новый пакет данных (0x71).
		self.PacketType = 0
		self.TableNumber = -1		# Флаг и номер, получена новая таблица (0xc2).
		self.ByteCount = 0
		self.PacketSize = 1 		# +1 байт типа пакета.
		# Первоначальное заполнение словаря.
		for Key in Parameters:
			self.TCU[Key[1]] = 0
			
		# Определение длины пакета.
		for Key in Parameters:
			if Key[0] == 'int8_t':
				self.PacketSize += 1
			elif Key[0] == 'uint8_t':
				self.PacketSize += 1
			elif Key[0] == 'int16_t':
				self.PacketSize += 2
			elif Key[0] == 'uint16_t':
				self.PacketSize += 2
	# Логирование
	def to_log(self, EmrtyLine = 0):
		LogLen = 10 * round(1000 / 50)		# Размер кольцового буфера с секундах (период 50мс).

		if self.LogCounter < 0:
			self.LogCounter = LogLen

		LogLine = ''
		# Записывает лог в кольцевой буфер.
		Date = datetime.now().strftime("%d.%m.%Y")
		Time = datetime.now().strftime("%H:%M:%S")
		Time += datetime.now().strftime(".%f")[:4]
		LogLine = Date + '\t' + Time + '\t'
		for Key in Parameters:
			LogLine += str(self.TCU[Key[1]]) + '\t'
		self.LogBuffer.append(LogLine)
		if len(self.LogBuffer) > LogLen:
			self.LogBuffer.pop(0)

		FileNameList = []		
		if self.WriteLog != 0:
			FileNameList.append(self.LogFile)
		if self.LogCounter > 0:
			FileNameList.append(self.LogFile + '_' + ('000' + str(self.LogNumber))[-3:])

		for FileName in FileNameList:
			# Проверка наличия файла лога.
			if not os.path.isfile(FileName):
				File = codecs.open(FileName, 'w', 'utf8')
				LogTitle = ''
				LogTitle = 'Date\tTime\t'
				for Key in Parameters:
					LogTitle += Key[1] + '\t'
				File.write(LogTitle + '\n')

				# Если запись была вызвана по кнопке, то записываем кольцевой буфер.
				for Line in self.LogBuffer:
					File.write(Line + '\n')

				File.close()
				EmrtyLine = 0

			File = codecs.open(FileName, 'a', 'utf8')
			if EmrtyLine == 1:
				File.write('\n')
			else:
				File.write(LogLine + '\n')
			File.close()

		if self.LogCounter > 0:
			self.LogCounter -= 1

	def get_com_ports(self, Mode):
		Ports = []
		for Port in serial.tools.list_ports.comports():
			if Mode == 0:
				Ports.append(Port.device)
			else:
				Ports.append(Port)
		return Ports

	def port_open(self, Port):
		#print(MainWindow.PortBox.get().split(' - ')[0])
		self.Serial.port = Port.split(' - ')[0]
		self.Serial.open()
		self.LogFile = self.LogFolder + 'AT_log_' + datetime.now().strftime("%Y-%m-%d_%H-%M") + '.log'
		self.to_log(1)
		self.PortReading = 1

	def port_close(self):
		self.PortReading = 0
		time.sleep(0.2)
		self.Serial.close()

	def port_status(self):
		# Закрывает отвалившееся соединение.
		if self.Serial.is_open and self.Serial.port not in self.get_com_ports(0):
			self.PortReading = 0
			self.port_close()
		if self.Serial.port in self.get_com_ports(0) and self.Serial.is_open:
			return 1
		else:
			return 0
		
	def data_update(self):
		self.NewData = 0
		self.PacketType = hex(self.get_uint8(0))
		ByteNumber = 1

		#if self.PacketType != '0x71':
		#	print(self.PacketType, self.ByteCount)
		#	print(self.DataArray)
		#	print(self.PacketType, self.get_uint8(ByteNumber) , self.ByteCount, self.PacketSize)
		
		# 0x71 - Пакет с параметрами ЭБУ.
		if self.PacketType == '0x71' and self.ByteCount == self.PacketSize:
			for Key in Parameters:
				Value = 0
				if Key[0] == 'int8_t':
					Value = self.get_int8(ByteNumber)
					ByteNumber += 1
				elif Key[0] == 'uint8_t':
					Value = self.get_uint8(ByteNumber)
					ByteNumber += 1
				elif Key[0] == 'int16_t':
					Value = self.get_int16(ByteNumber)
					ByteNumber += 2
				elif Key[0] == 'uint16_t':
					Value = self.get_uint16(ByteNumber)
					ByteNumber += 2
				self.TCU[Key[1]] = Value
			self.to_log()
			self.NewData = 1
		elif self.PacketType == '0xc2' and 	self.TableNumber == -1:
			self.TableNumber = self.get_uint8(ByteNumber)

			ByteNumber += 1
			N = self.TableNumber

			#print('0xc2')
			#print(self.ByteCount,  Tables[N][2] * 2 + 2)

			if self.ByteCount == Tables[N][2] * 2 + 2:
				self.TableData = []
				for i in range(Tables[N][2]):
					if Tables[N][1] == 'uint16_t':
						self.TableData.append(self.get_uint16(ByteNumber))
					elif Tables[N][1] == 'int16_t':
						self.TableData.append(self.get_int16(ByteNumber))
					ByteNumber += 2
				#print(self.TableNumber)
			else:
				self.TableNumber = -1 # Таблица не гожая.

	def get_int8(self, N):
		Value = ord(self.DataArray[N])
		if Value > 127:
			return Value - 256
		else:
			return Value
	def get_uint8(self, N):
		return ord(self.DataArray[N])
	def get_int16(self, N):
		return int.from_bytes(self.DataArray[N] + self.DataArray[N + 1], byteorder = 'little', signed = True)
	def get_uint16(self, N):
		return int.from_bytes(self.DataArray[N] + self.DataArray[N + 1], byteorder = 'little', signed = False)
	
	def send_command(self, Type, Table, Data):

		if self.PortReading != 1:
			return

		SendBuffer = []

		SendBuffer.append(0x40)	# Начало исходящего пакета.
		SendBuffer.append(Type)	# Тип пакета.
		self.add_byte(SendBuffer, Table)	# Номер таблицы.

		Signed = False
		if Tables[Table][1] == 'int16_t':
			Signed = True

		if Type == 0xc8:
			for Val in Data:
				for Byte in Val.to_bytes(2, 'big', signed = Signed):
					self.add_byte(SendBuffer, Byte)
		elif Type in (0xcc, 0xee, 0xab, 0xfc, 0xfd, 0xfe, 0xfa, 0xfb):
			SendBuffer.append(Type)	# Дополнительно вставляем тип пакета.
		elif Type == 0xbe:
			for Val in Data:
				for Byte in Val.to_bytes(1, 'big', signed = False):
					self.add_byte(SendBuffer, Byte)

		SendBuffer.append(0x0d)	# Конец пакета.
		#print(len(SendBuffer))
		SendBuffer = bytes(SendBuffer)
		#print('Send command', SendBuffer)
		self.Serial.write(SendBuffer)

	def add_byte(self, Array, Byte):	# Добавление байта с подменой.
		if Byte == 0x40:
			Array.append(0x0A)
			Array.append(0x82)
		elif Byte == 0x0D:
			Array.append(0x0A)
			Array.append(0x83)
		elif Byte == 0x0A:
			Array.append(0x0A)
			Array.append(0x84)
		else:
			Array.append(Byte)

	def read_port(self):
		while True:
			if self.PortReading == 1:
				Byte = self.Serial.read()
				#print(Byte)
				if self.Begin == 0:
					if Byte == b'\x40':
						self.DataArray = []
						self.Begin = 1
						self.ByteCount = 0
				elif self.Begin == 1:
					Replace = 0 
					if Byte == b'\x0a':
						Byte = self.Serial.read()
						Replace = 1
						if Byte == b'\x82':
							Byte = b'\x40'
						if Byte == b'\x83':
							Byte = b'\x0d'
						if Byte == b'\x84':
							Byte = b'\x0a'
					if Replace == 0 and Byte == b'\x0d':
						self.data_update()
						self.Begin = 0
					else:
						self.DataArray.append(Byte)
						self.ByteCount += 1
			else:
				time.sleep(0.2)