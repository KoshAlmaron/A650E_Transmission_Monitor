from tkinter import *
from tkinter import filedialog

import tkinter as tk

from datetime import datetime
import time
import json
import os

import ToolTip
import Tables

BackGroundColor = "#d0d0d0"

# Окно редактирования настроек.
class _DataExportEditWindow:
	def __init__(self, Uart, Ver):
		self.root = tk.Toplevel()
		self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.WindowOpen = 1
		self.WindowName = 'DataExport'

		self.ExportList = []

		self.Uart = Uart
		self.Version = Ver

		self.SleepStepTime = 0.010
		self.SleepStepCount = 25

		self.Width = 860
		self.Height = 710
		self.OffsetX = 20
		self.OffsetY = 0

		self.MainFont = font.Font(size = 10)
		self.root.option_add("*Font", self.MainFont)
		self.root.title('Экспорт/импорт калибровок')
		self.root.minsize(self.Width, self.Height)
		self.root.configure(background = BackGroundColor)

		self.SelectAllVar = IntVar()
		self.SelectAllVar.set(1)
		self.SelectAll = Checkbutton(self.root, text = '', variable = self.SelectAllVar, onvalue = 1, offvalue = 0, command = self.select_all, background = '#008080')
		self.SelectAll.place(x = 20, y = 18)

		# Экспорт в файл.
		self.ExportBtn = Button(self.root, text = "Экспорт\nв файл", width = 8, bg = "#4caa00", command = self.export_to_file, font = ("Helvetica", 12, 'bold'))
		self.ExportBtn.place(x = 60, y = 10)
		# Индикатор ответа ЭБУ.
		self.Answer = _LightIndicator(self.root, 'A', 167, 20)
		# Импорт из файла.
		self.ImportBtn = Button(self.root, text = "Импорт\nиз файла", width = 8, bg = "#1E90FF", command = self.import_from_file, font = ("Helvetica", 12, 'bold'))
		self.ImportBtn.place(x = 200, y = 10)

		self.WriteBtn = Button(self.root, text = "Отправить\nв ЭБУ", width = 9, bg = "#ff8c00", command = self.write_to_ram, font = ("Helvetica", 12, 'bold'), state = 'normal')
		self.WriteBtn.place(x = 330, y = 10)
		self.ESaveBtn = Button(self.root, text = "Отправить и\nсохранить в EEPROM", width = 19, bg = "#cd5500", command = self.save_to_eeprom, font = ("Helvetica", 12, 'bold'), state = 'disabled')
		self.ESaveBtn.place(x = 460, y = 10)

		# Добавление строк для экспорта/импорта.
		self.draw_paremeters()

		# Выход.
		self.ExitBtn = Button(self.root, text = "Закрыть", width = 12, height = 2, bg = "#cd853f", command = self.on_closing, font = ("Helvetica", 12, 'bold'))
		self.ExitBtn.place(x = self.Width - 145, y = 10)

		self.add_tooltip()

		self.BackupData = {
			'Version': '',
			'CreatedDate': '',
			'Config': {},
			'Tables': {}
		}

	def add_tooltip(self):	# Вставка подсказок.
		ToolTip.ToolTip(self.SelectAll, "Выделить всё / снять выделение.")
		ToolTip.ToolTip(self.ExportBtn, "Экспорт всех параметров ЭБУ в папку Backups в формате json.")
		ToolTip.ToolTip(self.Answer.Box, "Индикатор ответа ЭБУ на команду. Красный - команда не принята. Зелёный - команда успешно обработана.")
		ToolTip.ToolTip(self.ImportBtn, "Загрузка данных из файла во временный буфер. " + \
										"\nПосле загрузки все значения проверяются. " + \
										"\nПри наличии предупреждений блокируется кнопка записи в EEPROM." + \
										"\nПри критических ошибках блокируется загрузка блока данных.")

		ToolTip.ToolTip(self.WriteBtn, "Отправить выбранные параметры в ЭБУ без сохранения в EEPROM.")
		ToolTip.ToolTip(self.ESaveBtn, "Отправить выбранные параметры в ЭБУ и сохранить в EEPROM.")

	def draw_paremeters(self):
		self.Parameters = {}

		Y = 70
		DeltaY = 25
		BorderSpace = 5

		Border = ttk.Label(self.root, text = '', relief = "ridge", background = BackGroundColor)
		Border.place(x = 10, y = Y - 5, width = self.Width - 20, height = DeltaY * 2 + 3)

		self.add_row(Y, 'Config', 'Настройки АКПП')
		Y += DeltaY
		N = self.get_table_number('GearSpeedGraphs')
		self.add_row(Y, Tables.TablesData[N]['Table'], Tables.TablesData[N]['Name'])
		Y += DeltaY
		Y += BorderSpace

		Border = ttk.Label(self.root, text = '', relief = "ridge", background = BackGroundColor)
		Border.place(x = 10, y = Y - 5, width = self.Width - 20, height = DeltaY * 2 + 3)

		N = self.get_table_number('TPSGraph')
		self.add_row(Y, Tables.TablesData[N]['Table'], Tables.TablesData[N]['Name'])
		Y += DeltaY
		self.add_row(Y, Tables.TablesData[N + 1]['Table'], Tables.TablesData[N + 1]['Name'])
		Y += DeltaY
		Y += BorderSpace

		Border = ttk.Label(self.root, text = '', relief = "ridge", background = BackGroundColor)
		Border.place(x = 10, y = Y - 5, width = self.Width - 20, height = DeltaY * (len(Tables.TablesData) - 3) + 3)

		for K in range(0, N):
			self.add_row(Y, Tables.TablesData[K]['Table'], Tables.TablesData[K]['Name'])
			Y += DeltaY

		self.Height = Y + 10
		self.root.minsize(self.Width, self.Height)

	def add_row(self, Y, Name, FullName):
		Xc = 20
		Xt = 50

		RowDict = {}
		RowDict['Var'] = IntVar()

		Element = ttk.Label(self.root, text = FullName, width = 75, relief = "flat", background = BackGroundColor, font = ("Helvetica", 13))
		Element.place(x = Xt, y = Y)

		Element = Checkbutton(self.root, state = 'disabled', text = '', variable = RowDict['Var'], onvalue = 1, offvalue = 0, background = BackGroundColor)
		Element.place(x = Xc, y = Y - 4)

		RowDict['Element'] = Element
		self.Parameters[Name] = RowDict

	def get_table_number(self, Name):
		for n, Table in enumerate(Tables.TablesData):
			if Table['Table'] == Name:
				return n

	def select_all(self):
		for Key in self.Parameters:
			if self.Parameters[Key]['Element']['state'] == 'normal':
				self.Parameters[Key]['Var'].set(self.SelectAllVar.get())

	def import_from_file(self):
		# Выбор файла для загрузки.
		FilePath = tk.filedialog.askopenfilename (
			initialdir = self.get_backup_folder(),
			title = 'Выбор файла бэкапа',
			filetypes = (('Backup (*.json)', '*.json'), )
		)
		if not FilePath:
			return

		for Key in self.Parameters:
			self.Parameters[Key]['Var'].set(0)
			self.Parameters[Key]['Element'].configure(state = 'disabled')

		self.clear_backup_data()	# Очищаем структуру с данными.

		# Обработка файла.
		try:
			File = open(FilePath, "r", encoding="utf-8")
			Content = json.load(File)
		except Exception as error:
			messagebox.showerror('Импорт бэкапа', 'Не удалось прочитать файл:\n' + str(error))
			return

		ConfigWarn = ''
		ConfigErr = ''
		# Проверка конфигурации.
		if 'Config' in Content:
			for Key in Tables.ConfigData:
				if Key in Content['Config']:
					if (Content['Config'][Key] < Tables.ConfigData[Key]['Min']
					or Content['Config'][Key] > Tables.ConfigData[Key]['Max']):
						print(Content['Config'][Key])
						ConfigWarn += ' - Значение %s "%s" не попадает в диапазон от %s до %s\n' % (Key, Content['Config'][Key], Tables.ConfigData[Key]['Min'], Tables.ConfigData[Key]['Max'])
				else:
					ConfigErr += ' - Отсутствует обязательный параметр %s\n' % (Key)
			if ConfigErr == '':
				self.BackupData['Config'] = Content['Config'].copy()
				self.Parameters['Config']['Element'].configure(state = 'normal')
				self.Parameters['Config']['Var'].set(1)

		TablesWarn = ''
		TablesErr = ''
		if 'Tables' in Content:
			for Table in Tables.TablesData:
				TableOk = 1
				Name = Table['Table']
				if Name in Content['Tables']:
					ExpectedTableSize = len(Table['ArrayX'])
					if Table['Table'] == 'GearSpeedGraphs':
						ExpectedTableSize *= 8

					if len(Content['Tables'][Name]) != ExpectedTableSize:
						TablesErr += ' - Таблица %s имеет неправильную длину\n' % (Name)
						TableOk = 0
					else:
						for Value in Content['Tables'][Name]:
							if (Value < Table['Min']
							or Value > Table['Max']):
								TablesWarn += ' - Значение %s таблицы %s не попадает в диапазон от %s до %s\n' % (Value, Name, Table['Min'], Table['Max'])
				else:
					TablesWarn += ' - В бэкапе отсутствует таблица %s\n' % (Name)
					TableOk = 0
				if TableOk:
					self.BackupData['Tables'][Name] = Content['Tables'][Name].copy()
					self.Parameters[Name]['Element'].configure(state = 'normal')
					self.Parameters[Name]['Var'].set(1)

		Report = ''
		if ConfigWarn != '' or ConfigErr != '':
			Report += '\tКонфигурация:\n'
			Report += ConfigWarn
			Report += ConfigErr

		if TablesWarn != '' or TablesErr != '':
			Report += '\n\tТаблицы:\n'
			Report += TablesWarn
			Report += TablesErr

		self.ESaveBtn.configure(state = 'normal')
		if ConfigWarn != '' or TablesWarn != '':
			Report += '\n\nВ бэкапе есть кривые значения. Запись в EEPROM не доступна.\nПроверьте данные в соответсвующем окне и сохраните в EEPROM вручную.'
			self.ESaveBtn.configure(state = 'disabled')

		if Report == '':
			messagebox.showinfo('Проверка файла', 'Файл успешно загружен.')
		else:
			messagebox.showwarning('Проверка файла', Report)
		self.root.lift()

	def write_to_ram(self, EE = 0):
		for Config in Tables.ConfigData:
			Tables.ConfigData[Config]['Value'] = IntVar(value = 0)

		Count = 0
		for Key in self.Parameters:
			if self.Parameters[Key]['Element']['state'] == 'normal':
				if self.Parameters[Key]['Var'].get() == 1:
					Count += 1
					if Key == 'Config':
						# Копируем параметры из временного буфера в структуру конфигурации.
						for Cfg in Tables.ConfigData:
							 Tables.ConfigData[Cfg]['Value'].set(self.BackupData['Config'][Cfg])

						# Отправляем конфигурацию в ЭБУ.
						self.Answer.update(1)
						self.Uart.send_command('NEW_CONFIG_DATA', 0, [])

						# Ждем ответ ЭБУ.
						Result = self.wait_for_config()
						if Result == 1:
							messagebox.showwarning('Импорт бэкапа', 'Нет ответа от ЭБУ (Config)')
							return -1
						elif Result == 2:
							messagebox.showwarning('Импорт бэкапа', 'ЭБУ вернул неправильный данные (Config)')
							return -1

					else:
						TableN = self.get_table_number(Key)
						self.Answer.update(1)
						self.Uart.send_command('NEW_TABLE_DATA', TableN, self.BackupData['Tables'][Key])

						# Ждем ответ ЭБУ.
						Result = self.wait_for_table(Key)
						if Result == 1:
							messagebox.showwarning('Импорт бэкапа', 'Нет ответа от ЭБУ (' + Key + ')')
							return -1
						elif Result == 2:
							messagebox.showwarning('Импорт бэкапа', 'ЭБУ вернул неправильный данные (' + Key + ')')
							return -1

			self.Parameters[Key]['Var'].set(0)	# Убираем галочку для отображения прогресса.
			self.root.update_idletasks()		# Обновляем окно.

		if EE == 0:
			if Count > 0:
				messagebox.showinfo('Импорт бэкапа', 'Данные успешно отправленны в ЭБУ.\n(Без записи в EEPROM)')
			else:
				messagebox.showinfo('Импорт бэкапа', 'Не выбран ни один пункт для записи')
			self.root.lift()
		return 0

	def save_to_eeprom(self):
		ConfigBlock = 0
		SpeedBlock = 0
		ADCBlock = 0
		TablesBlock = 0

		# Проверяем данные каких блоков будут отправлены  в ЭБУ.
		for Key in self.Parameters:
			if self.Parameters[Key]['Element']['state'] == 'normal':
				if self.Parameters[Key]['Var'].get() == 1:
					if Key == 'Config':
						ConfigBlock = 1
					elif Key == 'GearSpeedGraphs':
						SpeedBlock = 1
					elif Key in ('TPSGraph', 'OilTempGraph'):
						ADCBlock = 1
					else:
						TablesBlock = 1

		# Отправляе данные в ЭБУ.
		self.write_to_ram(1)

		# Сохраняем по очереди каждый блок данных.
		if ConfigBlock:
			self.Answer.update(1)
			self.Uart.send_command('WRITE_EEPROM_CONFIG_COMMAND', 0, [])

			# Ждем ответ ЭБУ.
			Result = self.wait_for_config()
			if Result == 1:
				messagebox.showwarning('Сохранение в EEPROM', 'Нет ответа от ЭБУ (Конфигурация)')
				return
			elif Result == 2:
				messagebox.showwarning('Сохранение в EEPROM', 'ЭБУ вернул неправильный ответ (Конфигурация)')
				return

		if SpeedBlock:
			self.Answer.update(1)
			self.Uart.send_command('WRITE_EEPROM_SPEED_COMMAND', self.get_table_number('GearSpeedGraphs'), [])
			# Ждем ответ ЭБУ.
			Result = self.wait_for_table('GearSpeedGraphs')
			if Result == 1:
				messagebox.showwarning('Сохранение в EEPROM', 'Нет ответа от ЭБУ (Скорости переючения)')
				return
			elif Result == 2:
				messagebox.showwarning('Сохранение в EEPROM', 'ЭБУ вернул неправильный ответ (Скорости переючения)')
				return

		if ADCBlock:
			self.Answer.update(1)
			self.Uart.send_command('WRITE_EEPROM_ADC_COMMAND', self.get_table_number('TPSGraph'), [])
			# Ждем ответ ЭБУ.
			Result = self.wait_for_table('TPSGraph')
			if Result == 1:
				messagebox.showwarning('Сохранение в EEPROM', 'Нет ответа от ЭБУ (АЦП)')
				return
			elif Result == 2:
				messagebox.showwarning('Сохранение в EEPROM', 'ЭБУ вернул неправильный ответ (АЦП)')
				return

		if TablesBlock:
			self.Answer.update(1)
			self.Uart.send_command('WRITE_EEPROM_MAIN_COMMAND', self.get_table_number('SLTGraph'), [])
			# Ждем ответ ЭБУ.
			Result = self.wait_for_table('SLTGraph')
			if Result == 1:
				messagebox.showwarning('Сохранение в EEPROM', 'Нет ответа от ЭБУ (Таблицы)')
				return
			elif Result == 2:
				messagebox.showwarning('Сохранение в EEPROM', 'ЭБУ вернул неправильный ответ (Таблицы)')
				return

		if ConfigBlock == 1 or SpeedBlock == 1 or ADCBlock == 1 or TablesBlock == 1:
			messagebox.showinfo('Сохранение в EEPROM', 'Данные успешно сохранены в EEPROM)')
		else:
			messagebox.showinfo('Сохранение в EEPROM', 'Не выбран ни один пункт для сохранения')
		self.root.lift()

	def wait_for_config(self):
		# Ждем ответ ЭБУ, конфигурация.
		# Результат: 0 - всё ок, 1 - нет ответ, 2 - неправильный ответ.
		DataReceived = 0
		for T in range(0, self.SleepStepCount):
			if self.Uart.NewConfig == 1:
				self.Answer.update(0)
				self.Uart.NewConfig = 0
				DataReceived = 1
				break
			time.sleep(self.SleepStepTime)

		if DataReceived:
			if self.BackupData['Config'] != self.Uart.CFG:
				return 2
		else:
			return 1
		return 0

	def wait_for_table(self, TableName):
		# Ждем ответ ЭБУ, Таблицы.
		# Результат: 0 - всё ок, 1 - нет ответ, 2 - неправильный ответ.
		TableN = self.get_table_number(TableName)
		Steps = self.SleepStepCount
		if TableN == 0:
			Steps = 50

		DataReceived = 0
		for T in range(0, Steps):
			if self.Uart.TableNumber == TableN:
				self.Answer.update(0)
				self.Uart.TableNumber = -1
				DataReceived = 1
				break
			time.sleep(self.SleepStepTime)

		if DataReceived:
			if self.BackupData['Tables'][TableName] != self.Uart.TableData:
				return 2
		else:
			return 1
		return 0

	def export_to_file(self):
		self.ESaveBtn.configure(state = 'disabled')

		for Key in self.Parameters:
			self.Parameters[Key]['Var'].set(0)
			self.Parameters[Key]['Element'].configure(state = 'disabled')

		if not self.Uart.port_status():
			messagebox.showwarning('Экспорт бэкапа', 'Порт не открыт, экспорт невозможен.')
			return

		self.clear_backup_data()

		self.Answer.update(1)
		self.root.update_idletasks()
		self.Uart.NewConfig = 0
		self.Uart.send_command('GET_CONFIG_COMMAND', 0, [])

		DataReceived = 0
		for T in range(0, self.SleepStepCount):
			if self.Uart.NewConfig == 1:
				self.Answer.update(0)
				self.Uart.NewConfig = 0
				DataReceived = 1
				break
			time.sleep(self.SleepStepTime)

		if DataReceived:
			for Key in Tables.ConfigData:
				self.BackupData['Config'][Key] = self.Uart.CFG[Key]
			self.Parameters['Config']['Var'].set(1)
			self.root.update_idletasks()
		else:
			messagebox.showwarning('Экспорт бэкапа', 'Нет ответа от ЭБУ (Config)')
			return

		for Table in Tables.TablesData:
			self.Answer.update(1)
			self.root.update_idletasks()
			self.Uart.send_command('GET_TABLE_COMMAND', Table['N'], [])

			DataReceived = 0
			for T in range(0, self.SleepStepCount):
				if self.Uart.TableNumber == Table['N']:
					self.Answer.update(0)
					self.Uart.TableNumber = -1
					DataReceived = 1
					break
				time.sleep(self.SleepStepTime)

			ExpectedTableSize = len(Table['ArrayX'])
			if Table['Table'] == 'GearSpeedGraphs':
				ExpectedTableSize *= 8

			if DataReceived and len(self.Uart.TableData) == ExpectedTableSize:
				self.BackupData['Tables'][Table['Table']] = self.Uart.TableData.copy()

				self.Parameters[Table['Table']]['Var'].set(1)
				self.root.update_idletasks()
			else:
				messagebox.showwarning('Экспорт бэкапа', 'Нет ответа от ЭБУ (' + Table['Table'] + ')')
				return

		FileName = 'Backup_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.json'
		FilePath = os.path.join(self.get_backup_folder(), FileName)

		try:
			DumpText = self.format_backup_data(json.dumps(self.BackupData, ensure_ascii = False, indent = '\t'))
			File = open(FilePath, 'w', encoding = 'utf-8')
			File.write(DumpText)
			messagebox.showinfo('Экспорт бэкапа', 'Бэкап успешно сохранён в файл:\n' + FileName)
		except Exception as error:
			messagebox.showerror('Экспорт бэкапа', 'Не удалось сохранить бэкап:\n' + str(error))

	def clear_backup_data(self):

		self.BackupData['Version'] = self.Version
		self.BackupData['CreatedDate'] = datetime.now().isoformat(timespec = 'seconds')
		self.BackupData['Config'] = {}
		self.BackupData['Tables'] = {}

	def format_backup_data(self, DumpText):
		DumpText = DumpText.replace('[\n\t\t\t', '[')
		DumpText = DumpText.replace(',\n\t\t\t', ', ')
		DumpText = DumpText.replace('\n\t\t]', ']')
		return DumpText

	def get_backup_folder(self):
		Folder = os.path.join(os.getcwd(), "Backups")
		if not os.path.isdir(Folder):
			os.makedirs(Folderw, exist_ok = True)
		return Folder

	def on_closing(self):	# Событие по закрытию окна.
		self.WindowOpen = 0

	def window_close(self):	# Закрытие окна.
		self.root.destroy()

# Светофор.
class _LightIndicator:
	def __init__(self, root, Name, x, y):
		self.x = x
		self.y = y
		self.w = 25
		self.h = 25
		self.Name = Name
		self.StartColor = "#d0d0d0"
		self.OffColor = "#00ff33"
		self.OnColor = "#ff3333"

		# Холст.
		self.Box = Canvas(root, width = self.w, height = self.h, bg = BackGroundColor, bd = 0, highlightthickness = 0, relief = 'ridge')
		self.Box.place(x = self.x, y = self.y)
		# Круг
		self.Oval = self.Box.create_oval(0, 0, self.w - 1, self.h - 1, width = 2, fill = self.StartColor)
		# Название.
		self.Box.create_text(self.w / 2, self.h // 2, font = "Verdana 12 bold", justify = CENTER, fill = 'black', text = self.Name)
	def update(self, Value):
		if Value > 0:
			self.Box.itemconfig(self.Oval, fill = self.OnColor)
		else:
			self.Box.itemconfig(self.Oval, fill = self.OffColor)