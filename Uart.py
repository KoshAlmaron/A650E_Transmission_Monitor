import serial
import os
import threading
from datetime import datetime
import time
import serial.tools.list_ports
import codecs

import Tables

Parameters = (	  ('uint16_t', 'EngineRPM')
				, ('uint16_t', 'DrumRPM')
				, ('int16_t', 'DrumRPMDelta')
				, ('uint16_t', 'OutputRPM')
				, ('uint8_t', 'CarSpeed')
				, ('int16_t', 'OilTemp')
				, ('uint16_t', 'TPS')
				, ('uint16_t', 'InstTPS')
				, ('uint16_t', 'Load')
				, ('uint16_t', 'Barometer')
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
				, ('int8_t', 'AdaptationFlagTPS')
				, ('int8_t', 'AdaptationFlagTemp')
				, ('uint16_t', 'GearManualMode')
				)

CommandBytes = {'TCU_DATA_PACKET' :		0x71
				, 'GET_TABLE_COMMAND' :	0xc1
				, 'TCU_TABLE_ANSWER' :	0xc2
				, 'NEW_TABLE_DATA' :	0xc3

				, 'GET_CONFIG_COMMAND' :	0xc4
				, 'TCU_CONFIG_ANSWER' :		0xc5
				, 'NEW_CONFIG_DATA' :		0xc6

				, 'GET_PORTS_STATE' :		0xc7
				, 'PORTS_STATE_PACKET' :	0xc8

				, 'READ_EEPROM_MAIN_COMMAND' :		0xe0
				, 'READ_EEPROM_ADC_COMMAND' :		0xe1
				, 'READ_EEPROM_SPEED_COMMAND' :		0xe2
				, 'READ_EEPROM_CONFIG_COMMAND' :	0xe3

				, 'WRITE_EEPROM_MAIN_COMMAND' :		0xea
				, 'WRITE_EEPROM_ADC_COMMAND' :		0xeb
				, 'WRITE_EEPROM_SPEED_COMMAND' :	0xec
				, 'WRITE_EEPROM_CONFIG_COMMAND' :	0xed

				, 'SPEED_TEST_COMMAND' :	0xd0
				, 'GEAR_LIMIT_COMMAND' :	0xd1

				, 'TABLES_INIT_MAIN_COMMAND' :		0xda
				, 'TABLES_INIT_ADC_COMMAND' :		0xdb
				, 'TABLES_INIT_SPEED_COMMAND' :		0xdc
				, 'TABLES_INIT_CONFIG_COMMAND' :	0xdd

				, 'APPLY_G2_TPS_ADAPT_COMMAND' :		0xf0
				, 'APPLY_G2_TEMP_ADAPT_COMMAND' :		0xf1
				, 'APPLY_G2_ADV_ADAPT_COMMAND' :		0xf2
				, 'APPLY_G2_ADV_TEMP_ADAPT_COMMAND' :	0xf3

				, 'APPLY_G3_TPS_ADAPT_COMMAND' :	0xf4
				, 'APPLY_G3_TEMP_ADAPT_COMMAND' :	0xf5
}

# Прием данных по UART
class _uart:
	def __init__(self, Folder, Baudrate):
		self.TCU = {}				# Словарь с параметрами.
		self.CFG = {}				# Словарь с настройками.
		self.TableData = []			# Буфер для таблицы.
		self.PortData = []			# Буфер для состояния портов.
		self.Begin = 0				# Флаг начала пакета.
		self.DataArray = []			# Массив байт.
		self.LogFolder = Folder		# Папка с логами.
		self.LogFile = ''

		self.CRC = [0, 0]			# Контрольная сумма.
		
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
		
		self.PacketType = 0
		self.TableNumber = -1		# Флаг и номер, получена новая таблица (TCU_TABLE_ANSWER).
		self.ByteCount = 0
		self.DataPacketSize = 1 	# +1 байт типа пакета.
		self.PortPacketSize = 23 + 1

		self.dictionary_init()		# Инициаизация словарей.

		self.NewData = 1			# Флаг, получен новый пакет данных (TCU_DATA_PACKET).
		self.NewConfig = 0			# Флаг, получен новый пакет настроек (TCU_CONFIG_ANSWER).
		self.NewPortState = 0		# Флаг, получен новый пакет с портами (PORTS_STATE_PACKET).

	def dictionary_init(self):
		# Первоначальное заполнение словаря с параметрами.
		for Key in Parameters:
			self.TCU[Key[1]] = 0
			
		# Определение длины пакета.
		for Key in Parameters:
			if Key[0] == 'int8_t':
				self.DataPacketSize += 1
			elif Key[0] == 'uint8_t':
				self.DataPacketSize += 1
			elif Key[0] == 'int16_t':
				self.DataPacketSize += 2
			elif Key[0] == 'uint16_t':
				self.DataPacketSize += 2

		self.ConfigPacketSize = 1 		# +1 байт типа пакета.
		# Первоначальное заполнение словаря с настройками.
		for Key in Tables.ConfigData:
			self.CFG[Key] = 0

		# Определение длины пакета.
		for Key in Tables.ConfigData:
			if Tables.ConfigData[Key]['Type'] == 'int8_t':
				self.ConfigPacketSize += 1
			elif Tables.ConfigData[Key]['Type'] == 'uint8_t':
				self.ConfigPacketSize += 1
			elif Tables.ConfigData[Key]['Type'] == 'int16_t':
				self.ConfigPacketSize += 2
			elif Tables.ConfigData[Key]['Type'] == 'uint16_t':
				self.ConfigPacketSize += 2

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
		# Шлём несколько байт после открытия порта, чтобы МК переключился на нужный UART.
		self.Serial.write(bytes((0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff)))

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

	def crc_add(self, Value):
		self.CRC[0] += Value
		if self.CRC[0] > 255:
			self.CRC[0] -= 256
		
		self.CRC[1] += self.CRC[0];
		if self.CRC[1] > 255:
			self.CRC[1] -= 256

	def data_update(self):
		# Проверка CRC.
		self.CRC = [0, 0]

		for i in range(0, self.ByteCount - 2):
			self.crc_add(self.get_uint8(i))
		self.crc_add(self.ByteCount - 2)

		if self.get_uint8(self.ByteCount - 2) != self.CRC[0] or self.get_uint8(self.ByteCount - 1) != self.CRC[1]:
			print('Ошибка CRC!')
			return

		self.ByteCount -= 2		# Два байта CRC.
		self.NewData = 0
		self.PacketType = self.get_uint8(0)
		ByteNumber = 1

		# if self.PacketType != CommandBytes['TCU_DATA_PACKET']:
		# 	print(self.PacketType, self.ByteCount)
		# 	print(self.DataArray)
		# 	print(self.PacketType, self.get_uint8(ByteNumber) , self.ByteCount, self.DataPacketSize)
		# print(self.PacketType, CommandBytes['TCU_DATA_PACKET'], self.ByteCount, self.DataPacketSize)

		# 0x71 - Пакет с параметрами ЭБУ.
		if self.PacketType == CommandBytes['TCU_DATA_PACKET'] and self.ByteCount == self.DataPacketSize:
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

		# Пакет с состоянием портов.
		if self.PacketType == CommandBytes['PORTS_STATE_PACKET'] and self.ByteCount == self.PortPacketSize:
			self.PortData = []

			for i in range(0, self.PortPacketSize - 1):
				self.PortData.append(self.get_uint8(ByteNumber + i))
			self.NewPortState = 1

		# Пакет с настройками ЭБУ.
		elif self.PacketType == CommandBytes['TCU_CONFIG_ANSWER'] and self.ByteCount == self.ConfigPacketSize:
			for Key in Tables.ConfigData:
				Value = 0
				if Tables.ConfigData[Key]['Type'] == 'int8_t':
					Value = self.get_int8(ByteNumber)
					ByteNumber += 1
				elif Tables.ConfigData[Key]['Type'] == 'uint8_t':
					Value = self.get_uint8(ByteNumber)
					ByteNumber += 1
				elif Tables.ConfigData[Key]['Type'] == 'int16_t':
					Value = self.get_int16(ByteNumber)
					ByteNumber += 2
				elif Tables.ConfigData[Key]['Type'] == 'uint16_t':
					Value = self.get_uint16(ByteNumber)
					ByteNumber += 2
				self.CFG[Key] = Value
			self.to_log()
			self.NewConfig = 1
			#print(self.CFG)

		# Пакет с таблицей.
		elif self.PacketType == CommandBytes['TCU_TABLE_ANSWER'] and self.TableNumber == -1:
			self.TableNumber = self.get_uint8(ByteNumber)

			ByteNumber += 1
			N = self.TableNumber

			if self.ByteCount == Tables.TablesData[N]['Size'] + 2:
				self.TableData = []

				if Tables.TablesData[N]['Type']	 == 'uint16_t':
					for i in range(Tables.TablesData[N]['Size']	 // 2):
						self.TableData.append(self.get_uint16(ByteNumber + i * 2))
				elif Tables.TablesData[N]['Type']	 == 'int16_t':
					for i in range(Tables.TablesData[N]['Size']	 // 2):
						self.TableData.append(self.get_int16(ByteNumber + i * 2))

				if Tables.TablesData[N]['Type']	 == 'uint8_t':
					for i in range(Tables.TablesData[N]['Size']	):
						self.TableData.append(self.get_uint8(ByteNumber + i))
				elif Tables.TablesData[N]['Type']	 == 'int8_t':
					for i in range(Tables.TablesData[N]['Size']	):
						self.TableData.append(self.get_int8(ByteNumber + i))
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
	
	def send_command(self, Command, Table, Data):
		if self.PortReading != 1:
			return

		N = Table
		Command = CommandBytes[Command]
		SendBuffer = []

		SendBuffer.append(0x40)			# Начало исходящего пакета.
		SendBuffer.append(Command)		# Тип пакета.
		SendBuffer.append(N)			# Номер таблицы.

		Signed = False
		if Tables.TablesData[N]['Type']	 == 'int16_t' or Tables.TablesData[N]['Type']	 == 'int8_t':
			Signed = True

		ValSize = 2
		if Tables.TablesData[N]['Type']	 == 'uint8_t' or Tables.TablesData[N]['Type'] == 'int8_t':
			ValSize = 1

		if Command == CommandBytes['NEW_TABLE_DATA']:
			for Val in Data:
				for Byte in Val.to_bytes(ValSize, 'big', signed = Signed):
					SendBuffer.append(Byte)
		elif Command == CommandBytes['GEAR_LIMIT_COMMAND']:
			for Val in Data:
				for Byte in Val.to_bytes(1, 'big', signed = False):
					SendBuffer.append(Byte)

		elif Command == CommandBytes['NEW_CONFIG_DATA']:
			for Key in Tables.ConfigData:
				Value = int(Tables.ConfigData[Key]['Value'].get())
				ValSize = 1
				Signed = False

				if Tables.ConfigData[Key]['Type'] == 'uint16_t' or Tables.ConfigData[Key]['Type']	 == 'int16_t':
					ValSize = 2
				if Tables.ConfigData[Key]['Type'] == 'int8_t' or Tables.ConfigData[Key]['Type']	 == 'int16_t':
					Signed = True

				for Byte in Value.to_bytes(ValSize, 'little', signed = Signed):
					SendBuffer.append(Byte)

		else:
			SendBuffer.append(Command)	# Дополнительно вставляем тип пакета.

		# Добавляем CRC.
		self.CRC = [0, 0]
		for i in range(1, len(SendBuffer)):	# Исключаем первый байт начала пакета 0x40.
			self.crc_add(SendBuffer[i])
		self.crc_add(len(SendBuffer) - 1)

		SendBuffer.append(self.CRC[0])
		SendBuffer.append(self.CRC[1])

		SendBuffer = self.format_send_packet(SendBuffer)

		SendBuffer.append(0x0d)	# Конец пакета.

		CommandStr = ''
		for b in SendBuffer:
			CommandStr += ', ' + hex(b)
		CommandStr = CommandStr[2:]
		#print(CommandStr)

		SendBuffer = bytes(SendBuffer)
		self.Serial.write(SendBuffer)

	def format_send_packet(self, Array):	# проверка пакета на наличие спецсимволов.
		Result = []
		Result.append(Array[0])
		for i in range(1, len(Array)):
			if Array[i] == 0x40:
				Result.append(0x0A)
				Result.append(0x82)
			elif Array[i] == 0x0D:
				Result.append(0x0A)
				Result.append(0x83)
			elif Array[i] == 0x0A:
				Result.append(0x0A)
				Result.append(0x84)
			else:
				Result.append(Array[i])
		return Result

	def read_port(self):
		while True:
			if self.PortReading == 1 and self.Serial.is_open:
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