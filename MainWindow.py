from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import messagebox

import math
import json
import os

import Tables
import ToolTip

ConfigFilePath = os.path.join(os.getcwd(), "Config.json")

GraphNames = (('---', 100)
	, ('EngineRPM', 6000)
	, ('DrumRPM', 6000)
	, ('DrumRPMDelta', 1200)
	, ('OutputRPM', 6000)
	, ('CarSpeed' , 150)
	, ('InstTPS', 100)
	, ('TPS', 100)
	, ('Load', 100)
	, ('Barometer', 1200)
	, ('SLT', 1023)
	, ('SLN', 1023)
	, ('SLU', 1023)
	, ('S1', 2)
	, ('S2', 2)
	, ('S3', 2)
	, ('S4', 2)
	, ('Gear', 5))

ATModeChar = ('I', 'P', 'R', 'N', 'D', 'D4', 'D3', 'L2', 'L', 'E', 'M')
BackGroundColor = "#d0d0d0"

# Главное окно.
class _MainWindow:
	def __init__(self, Ver, Uart):
		self.root = Tk()
		self.Uart = Uart
		self.EditTables = 0
		self.EditADC = 0
		self.EditSpeed = 0
		self.EditConfig = 0
		self.DataExport = 0
		self.PortState = 0

		Width = 1300
		Height = 700
		OffsetX = (self.root.winfo_screenwidth() - Width) // 2
		OffsetY = 0

		self.root.title('Мониторинг работы АКПП (' + Ver + ')')
		self.root.geometry(f'{Width}x{Height}+{OffsetX}+{OffsetY}')
		self.root.configure(background = BackGroundColor)

		MainFont = font.Font(size = 16)
		self.root.option_add("*Font", MainFont)

		self.load_config()

		ComPorts = self.Uart.get_com_ports(1)
		self.PortBox = ttk.Combobox(values = ComPorts, state = "readonly", width = 36)
		self.PortBox.place(x = 25, y = Height-50)

		ActivePort = -1
		for N, Port in enumerate(ComPorts):
			if Port[0] == Tables.Configuration['LastUsedPort']:
				ActivePort = N
		if ActivePort >= 0:
			self.PortBox.current(ActivePort)

		self.PortBtn = Button(text = "Старт", width = 10, bg = "#fb7b72", command = self.port_start_stop)
		self.PortBtn.place(x = 25, y = Height-100)

		self.ConfigBtn = Button(text = "Настройки", width = 9, bg = "#3CB371", command = self.edit_config, state='normal')
		self.ConfigBtn.place(x = 580, y = Height-55)

		self.TablesBtn = Button(text = "Таблицы", width = 8, bg = "#1e90ff", command = self.edit_tables, state='normal')
		self.TablesBtn.place(x = 760, y = Height-55)

		self.ExportBtn = Button(text = "Экспорт/Импорт", width = 14, bg = "#a0522d", command = self.data_export, state='normal')
		self.ExportBtn.place(x = 925, y = Height-55)

		self.ExitBtn = Button(text = "Выход", width = 6, height = 2, bg = "#f1e71f", command = self.quit)
		self.ExitBtn.place(x = 1188, y = Height-80)

		# Галка "Записывать лог".
		self.WriteLog = IntVar()
		self.WriteLogChk = Checkbutton(self.root, text='Записывать лог', command = self.set_log_status, variable = self.WriteLog, onvalue = 1, offvalue = 0, background = BackGroundColor, font = ("Helvetica", 14, 'bold'))
		self.WriteLogChk.place(x = 200, y = Height-90)
		self.WriteLog.set(0)

		self.LogBtn = Button(text = "Лог-метка", width = 8, bg = "#D2B48C", command = self.write_log)
		self.LogBtn.place(x = 400, y = Height-85, height = 30)

		#				       			  Name  x,  y min max, 	color
		self.SLT = _LineMeter(self.root, 'SLT', 30, 30, 0, 1023, '#1000fd')
		self.SLN = _LineMeter(self.root, 'SLN', 160, 30, 0, 1023, '#1000fd')
		self.SLU = _LineMeter(self.root, 'SLU', 290, 30, 0, 1023, '#1000fd')
		
		self.S1 = _LightIndicator(self.root, 'S1', 20, 360, '#00bd00')
		self.S2 = _LightIndicator(self.root, 'S2', 110, 360, '#00ad00')
		self.S3 = _LightIndicator(self.root, 'S3', 200, 360, '#00bd00')
		self.S4 = _LightIndicator(self.root, 'S4', 290, 360, '#00bd00')

		self.OIL = _RoundMeter(self.root, 'OIL', 400, 20, -30, 150, 'white')
		self.TPS = _RoundMeter(self.root, 'TPS', 700, 20, 0, 100, 'white')
		self.SPD = _RoundMeter(self.root, 'SPD', 1000, 20, 0, 160, 'white')

		self.ADCBtn = Button(text = "АЦП", width = 4, bg = "#0080a0", command = self.edit_adc, state='normal')
		self.ADCBtn.place(x = 655, y = 10)

		self.SpeedBtn = Button(text = "Скорость", width = 8, bg = "#FF8C00", command = self.edit_speed, state='normal')
		self.SpeedBtn.place(x = 924, y = 10)

		self.IOBtn = Button(text = "I/O", width = 4, bg = "#e0e0ff", command = self.port_state, state='normal', font = ("Helvetica", 12, 'bold'))
		self.IOBtn.place(x = 515, y = 185)

		self.BRK = _LightIndicator(self.root, 'BRK', 20, 500, '#ff7070')
		self.ENG = _LightIndicator(self.root, 'ENG', 110, 500, '#ffd700')
		self.LCK = _LightIndicator(self.root, 'LCK', 200, 500, '#4882b4')
		self.SLP = _LightIndicator(self.root, 'SLP', 290, 500, '#ff0000')

		self.Selector = _TextIndicator(self.root, 65, 430, '#efffef')
		self.ATMode = _TextIndicator(self.root, 155, 430, '#efffef')
		self.Gear = _TextIndicator(self.root, 245, 430, '#efffef')
		
		self.MainGraph = _Graph(self.root, 450, 230, Uart)

		self.SpdTest = Button(text = "Тест", width = 4, bg = "#e0ffe0", command = self.speed_test, state='normal', font = ("Helvetica", 12, 'bold'))
		self.SpdTest.place(x = 1115, y = 185)

		self.AdaptTemp = _AdaptationIndicator(self.root, 680 , 80)
		self.AdaptTPS = _AdaptationIndicator(self.root, 980 , 80)

		self.add_tooltip()

		self.set_log_status()

	def set_log_status(self):
		if self.WriteLog.get() == 1:
			self.Uart.WriteLog = 1
		else:
			self.Uart.WriteLog = 0

	def write_log(self):
		self.Uart.LogCounter = -1
		self.Uart.LogNumber += 1

	def add_tooltip(self):
		ToolTip.ToolTip(self.PortBox, "Выбор COM-порта ЭБУ")
		ToolTip.ToolTip(self.PortBtn, "Старт/Стоп COM-порта")

		ToolTip.ToolTip(self.TablesBtn, "Открыть окно редактирования графиков.")
		ToolTip.ToolTip(self.ADCBtn, "Открыть окно настройки датчиков")
		ToolTip.ToolTip(self.SpeedBtn, "Открыть окно настройки скоростей переключения передач")
		ToolTip.ToolTip(self.ConfigBtn, "Открыть окно настроек")

		ToolTip.ToolTip(self.ExportBtn, "Открыть окно экспорта/импорта ккалибровок")
		ToolTip.ToolTip(self.IOBtn, "Открыть окно просмотра состояний портов МК")

		ToolTip.ToolTip(self.ExitBtn, "Закрыть программу")

		ToolTip.ToolTip(self.SLT.Box, "Линейное давление SLT. Основное давление масла в системе.")
		ToolTip.ToolTip(self.SLN.Box, "Давление (величина сброса давления) подпора гидроаккумуляторов SLN. В простое давление максимальное, при переключениях устанавливается в соотвествии с графиком.")
		ToolTip.ToolTip(self.SLU.Box, "Давление SLU. Используется для блокировки ГТ и работы тормоза B3 второй передачи.")

		ToolTip.ToolTip(self.S1.Box, "Состояние шифтового соленоида S1.")
		ToolTip.ToolTip(self.S2.Box, "Состояние шифтового соленоида S2.")
		ToolTip.ToolTip(self.S3.Box, "Состояние шифтового соленоида S3.")
		ToolTip.ToolTip(self.S4.Box, "Состояние шифтового соленоида S4.")

		ToolTip.ToolTip(self.OIL.Box, "Температура масла.")
		ToolTip.ToolTip(self.TPS.Box, "Текущее значение ДПДЗ.")
		ToolTip.ToolTip(self.SPD.Box, "Скорость автомобиля.\nСиние стрелки - это пороги переключения текущей передачи.")
		
		ToolTip.ToolTip(self.BRK.Box, "Состояние педали тормоза. Без тормоза при переключении N->R задняя передача не включится. При нажатии тормоза на ходу происходит разблокировка ГТ")
		ToolTip.ToolTip(self.ENG.Box, "Флаг работы двигателя. При неработающем двигателе отключаются все соленоиды и сбрасывается состояние АКПП.")

		ToolTip.ToolTip(self.LCK.Box, "Состояние блокировки ГТ.")
		ToolTip.ToolTip(self.SLP.Box, "Обнаружение проскальзывание фрикционов. Контроль производится по оборотам входного/выходного валов и передаточного числа текущей передачи")

		ToolTip.ToolTip(self.Selector.Box, "Положение селектора. I - инициализация при старте, E - ошибка")
		ToolTip.ToolTip(self.ATMode.Box, "Состояние АКПП. I - инициализация при старте, E - ошибка")
		ToolTip.ToolTip(self.Gear.Box, "Текущая передача.")

		ToolTip.ToolTip(self.SpdTest, " Устанавливает скорость 100 км/ч для теста.")

		ToolTip.ToolTip(self.LogBtn, "Запись части лога (+- 10 секунд от нажатия) в отдельный файл. Работает даже при отключенном основном логировании.")

		ToolTip.ToolTip(self.AdaptTPS.Box, "Индикатор срабатывания адаптации по ДПДЗ.")
		ToolTip.ToolTip(self.AdaptTemp.Box, "Индикатор срабатывания адаптации по температуре.")

	def update(self):
		self.SLT.update(self.Uart.TCU['SLT'])
		self.SLN.update(self.Uart.TCU['SLN'])
		self.SLU.update(self.Uart.TCU['SLU'])

		self.S1.update(self.Uart.TCU['S1'])
		self.S2.update(self.Uart.TCU['S2'])
		self.S3.update(self.Uart.TCU['S3'])
		self.S4.update(self.Uart.TCU['S4'])
		
		self.OIL.update(self.Uart.TCU['OilTemp'])
		self.TPS.update(self.Uart.TCU['InstTPS'])
		self.SPD.update(self.Uart.TCU['CarSpeed'])

		self.SPD.update_markers(self.SPD.MarkerMin, self.Uart.TCU['GearDownSpeed'])
		self.SPD.update_markers(self.SPD.MarkerMax, self.Uart.TCU['GearUpSpeed'])
		
		self.BRK.update(self.Uart.TCU['Break'])
		self.ENG.update(self.Uart.TCU['EngineWork'])
		self.LCK.update(self.Uart.TCU['Glock'])
		self.SLP.update(self.Uart.TCU['SlipDetected'])
		
		if self.Uart.TCU['GearManualMode'] > 0:
			self.Uart.TCU['ATMode'] = 10
		self.Selector.update(ATModeChar[self.Uart.TCU['Selector']])
		self.ATMode.update(ATModeChar[self.Uart.TCU['ATMode']])
		
		Gear = self.Uart.TCU['Gear']
		if Gear == 0:
			Gear = 'N'
		elif Gear == -1:
			Gear = 'R'
		self.Gear.update(Gear)

		self.AdaptTPS.update(self.Uart.TCU['AdaptationFlagTPS'])
		self.AdaptTemp.update(self.Uart.TCU['AdaptationFlagTemp'])

		self.MainGraph.update()

	def update_graph_data(self):
		self.MainGraph.update_data()

	def edit_tables(self):
		self.EditTables = 1

	def edit_adc(self):
		self.EditADC = 1

	def edit_speed(self):
		self.EditSpeed = 1

	def edit_config(self):
		self.EditConfig = 1

	def data_export(self):
		self.DataExport = 1

	def port_state(self):
		self.PortState = 1

	def speed_test(self):
		self.Uart.send_command('SPEED_TEST_COMMAND', 0, [])

	def port_start_stop(self):
		if self.Uart.port_status():
			self.Uart.port_close()
			for key in self.Uart.TCU:
				self.Uart.TCU[key] = 0
			self.update()
			self.port_update()
		else:
			self.Uart.port_open(self.PortBox.get())
			Tables.Configuration['LastUsedPort'] = self.PortBox.get().split(' - ')[0]
			self.port_update()

	def port_update(self):
		ComPorts = self.Uart.get_com_ports(1)
		self.PortBox.config(values = ComPorts)

		if self.Uart.port_status():
			self.PortBtn.config(background = "#54fa9b", text = 'Стоп')
			#self.TablesBtn.config(state='normal')
		else:
			self.PortBtn.config(background = "#fb7b72", text = 'Старт')
			#self.TablesBtn.config(state='disabled')

	def load_config(self):
			# Обработка файла.
		try:
			File = open(ConfigFilePath, "r", encoding="utf-8")
			Tables.Configuration = json.load(File)
		except Exception as error:
			messagebox.showerror('Загрузка конфигурации', 'Не удалось прочитать файл конфигурации:\n' + str(error))
			return

	def save_config(self):
		DumpText = json.dumps(Tables.Configuration, ensure_ascii = False, indent = '\t')
		File = open(ConfigFilePath, 'w', encoding = 'utf-8')
		File.write(DumpText)

	def quit(self):
		self.save_config()
		self.Uart.PortReading = 0
		self.root.destroy()
		exit()

# Линейная шкала
class _LineMeter:
	def __init__(self, root, Name, x, y, min, max, Color):
		self.Value = 0
		self.x = x
		self.y = y
		self.w = 50
		self.h = 255
		self.min = min
		self.max = max
		self.Color = Color
		self.OffsetY = 30
		
		# Холст.
		self.Box = Canvas(root, width = self.w + 50, height = self.h + 65, bg = "#d0d0d0", bd = 0, highlightthickness = 0, relief = 'ridge')
		self.Box.place(x = self.x, y = self.y)
		# Название.
		self.Box.create_text(self.w / 2, 15, font = "Verdana 15 bold", justify = CENTER, fill = 'black', text = Name)
		# Двойная рамка.
		self.Box.create_rectangle(0, self.OffsetY, self.w, self.h + self.OffsetY + 4, fill = None)
		self.Box.create_rectangle(1, self.OffsetY + 1, self.w - 1, self.h + self.OffsetY + 3, fill = 'white')
		# Колбаса.
		self.Gauge = self.Box.create_rectangle(0, 0, 0, 0, fill = self.Color, outline = self.Color)
		# Подпись.
		self.TextValue = self.Box.create_text(25, self.h + self.OffsetY + 19, font = "Verdana 14", justify = CENTER, fill = 'black', text = str(self.Value))
		# Риски значений.
		self.Box.create_line(self.w, self.OffsetY + 1, self.w + 12, self.OffsetY + 1, fill = 'black', width = 2)
		self.Box.create_text(self.w + 30, self.OffsetY + 1, font = "Verdana 12", justify = CENTER, fill = 'black', text = str(self.max))
		self.Box.create_line(self.w, self.h / 4 + self.OffsetY + 3, self.w + 6, self.h / 4 + self.OffsetY + 3, fill = 'black', width = 2)
		self.Box.create_line(self.w, self.h / 2 + self.OffsetY + 3, self.w + 12, self.h / 2 + self.OffsetY + 3, fill = 'black', width = 2)
		self.Box.create_text(self.w + 30, self.h / 2 + self.OffsetY + 3, font = "Verdana 12", justify = CENTER, fill = 'black', text = str((self.min + self.max) // 2))
		self.Box.create_line(self.w, self.h * 3 / 4 + self.OffsetY + 3, self.w + 6, self.h * 3 / 4 + self.OffsetY + 3, fill = 'black', width = 2)
		self.Box.create_line(self.w, self.h + self.OffsetY + 4, self.w + 12, self.h + self.OffsetY + 4, fill = 'black', width = 2)
		self.Box.create_text(self.w + 24, self.h + self.OffsetY + 4, font = "Verdana 12", justify = CENTER, fill = 'black', text = str(self.min))

	def update(self, Value):
		# Обновление колбасы.
		if Value == 0:
			self.Box.coords(self.Gauge, 0, 0, 0, 0)
		else:
			x1 = 2
			x2 = self.w - 2
			y1 = self.h + self.OffsetY + 2 - (Value * self.h) / self.max
			y2 = self.h + self.OffsetY + 2
			self.Box.coords(self.Gauge, x1, y1, x2, y2)
		# Обновление подписи.
		self.Box.itemconfig(self.TextValue, text = str(Value))

# Текстовый индикатор.
class _TextIndicator:
	def __init__(self, root, x, y, Color):
		self.x = x
		self.y = y
		self.w = 70
		self.h = 70

		self.Color = Color
		
		# Холст.
		self.Box = Canvas(root, width = self.w, height = self.h, bg = BackGroundColor, bd = 0, highlightthickness = 0, relief = 'ridge')
		self.Box.place(x = self.x, y = self.y)
		# Круг
		self.Oval = self.Box.create_oval (0, 0, self.w - 1, self.h - 1, width = 2, fill = Color)
		# Текст.
		self.TextVal = self.Box.create_text(self.w / 2, self.h // 2, font = "Serif 20 bold", justify = CENTER, fill = 'black', text = '')
	def update(self, Text):
		self.Box.itemconfig(self.TextVal, text = str(Text))
		if Text == 'E':
			self.Box.itemconfig(self.Oval, fill = '#ff4040')
		else:
			self.Box.itemconfig(self.Oval, fill = self.Color)

# Круговая шкала
class _RoundMeter:
	def __init__(self, root, Name, x, y, min, max, Color):
		self.x = x
		self.y = y
		self.min = min
		self.max = max
		self.r = 100
		self.Offset = 45
		self.Name = Name
		self.Color = Color
		
		# Холст.
		self.Box = Canvas(root, width = self.r * 2 + self.Offset * 2, height = self.r * 1.6, bg = BackGroundColor, bd = 0, highlightthickness = 0, relief = 'ridge')
		self.Box.place(x = self.x, y = self.y)
		# Круг
		self.Box.create_oval (1 + self.Offset, 1 + self.Offset, self.r * 2 - 1 + self.Offset, self.r * 2 - 1 + self.Offset, width = 2, fill = Color)
		self.Box.create_rectangle(0, self.r + self.Offset, self.r * 2 + self.Offset, self.r * 2 + self.Offset, fill = BackGroundColor, outline = BackGroundColor)
		# Маркеры.
		self.MarkerMin = self.Box.create_line(0, 0, 0, 0, width = 1.5, dash = 3,  fill = 'blue')
		self.MarkerMax = self.Box.create_line(0, 0, 0, 0, width = 1.5, dash = 3, fill = 'blue')
		# Стрелка.
		self.Box.create_oval (self.r - 10 + self.Offset, self.r - 10 + self.Offset, self.r + 10 + self.Offset, self.r + 10 + self.Offset, width = 1, fill = 'black')
		self.Needle = self.Box.create_line(0, 0, 0, 0, width = 3, fill = 'black')

		# Значение.
		self.TextValue = self.Box.create_text(self.r + self.Offset, self.r, font = "Verdana 14", justify = CENTER, fill = 'black', text = '0')
		self.update(self.min)

		# Подписи
		self.print_line(self.min, 12, 1)
		self.print_line(self.min + (self.max - self.min) // 2, 12, 1)
		self.print_line(self.max, 12, 1)
		self.print_line(self.min + (self.max - self.min) // 4, 12, 1)
		self.print_line(self.min + (self.max - self.min) * 3 // 4, 12, 1)
		self.print_line(self.min + (self.max - self.min) * 1 // 8, 8, 0)
		self.print_line(self.min + (self.max - self.min) * 3 // 8, 8, 0)
		self.print_line(self.min + (self.max - self.min) * 5 // 8, 8, 0)
		self.print_line(self.min + (self.max - self.min) * 7 // 8, 8, 0)
		# Название.
		self.Box.create_text(self.r + self.Offset, 0 + 10, font = "Verdana 18 bold", justify = CENTER, fill = 'black', text = self.Name)

	def print_line(self, Value, Leght, Text = 1):
		Angle = 180 * ((Value - self.min) / (self.max - self.min))
		Rads = (Angle + 180) * (math.pi / 180)
		x1 = (self.r - 1) * math.cos(Rads) + self.r + self.Offset;
		y1 = (self.r - 1) * math.sin(Rads) + self.r + self.Offset;
		x2 = (self.r - Leght) * math.cos(Rads) + self.r + self.Offset;
		y2 = (self.r - Leght) * math.sin(Rads) + self.r + self.Offset;
		self.Box.create_line(x1, y1, x2, y2, width = 2, fill = 'black')
		if Text:
			self.Box.create_text(x1 + (20 * math.cos(Rads)), y1 + (14 * math.sin(Rads)), font = "Verdana 12", justify = CENTER, fill = 'black', text = str(Value))

	def update(self, Value):
		Angle = 180 * ((Value - self.min) / (self.max - self.min))
		Rads = (Angle + 180) * (math.pi / 180)
		x = (self.r - 15) * math.cos(Rads) + self.r + self.Offset;
		y = (self.r - 15) * math.sin(Rads) + self.r + self.Offset;
		self.Box.coords(self.Needle, self.r + self.Offset, self.r + self.Offset, x, y)
		# Обновление значения.
		self.Box.itemconfig(self.TextValue, text = str(Value))

	def update_markers(self, Marker, Value):
		Angle = 180 * ((Value - self.min) / (self.max - self.min))
		Rads = (Angle + 180) * (math.pi / 180)

		x = (self.r - 15) * math.cos(Rads) + self.r + self.Offset;
		y = (self.r - 15) * math.sin(Rads) + self.r + self.Offset;

		self.Box.coords(Marker, self.r + self.Offset, self.r + self.Offset, x, y)

class _Graph:
	def __init__(self, root, x, y, Uart):
		self.x = x
		self.y = y
		self.Uart = Uart
		self.min = 0
		self.max = 100
		self.w = 780
		self.h = 320
		self.Border = 10
		
		# Маштаб
		self.ScaleLabel = ttk.Label(text = "Маштаб", width = 15, anchor = CENTER, background = BackGroundColor)
		self.ScaleLabel.place(x = self.x + self.w / 2 - 150, y = self.y - 40)
		self.ScaleBox = ttk.Combobox(values = (1, 2, 4), state = "readonly", width = 1)
		self.ScaleBox.current(1)
		self.ScaleBox.place(x = self.x + self.w / 2 + 10, y = self.y - 40)
		
		# Холст.
		self.Box = Canvas(root, width = self.w + 55, height = self.h, bg = BackGroundColor, bd = 0, highlightthickness = 0, relief = 'ridge')
		self.Box.place(x = self.x, y = self.y)
		
		Names = []
		for Name in GraphNames:
			Names.append(Name[0])
			
		self.Colors = ('green', 'blue', 'brown','red' ,'purple')
		self.GraphArrays = []

		for i in range(len(self.Colors)):
			Array = []
			for k in range(self.w - self.Border * 2):
				Array.append(0)
			self.GraphArrays.append(Array)

		self.ComboboxArray = []
		for i in range(len(self.Colors)):
			self.ComboboxArray.append(self.add_listbox(i, Names))
		self.ComboboxArray[0].current(0)
		self.ComboboxArray[1].current(0)
		self.ComboboxArray[2].current(0)
		self.ComboboxArray[3].current(0)
		self.ComboboxArray[4].current(0)

	def add_listbox(self, n, Names):
		Combobox_1 = ttk.Combobox(values = Names, state = "readonly", width = 9, foreground = self.Colors[n])
		Combobox_1.current(0)
		Combobox_1.place(x = self.x + n * 158, y = self.y + self.h + 20)
		return Combobox_1
		
	def print_line(self, Value, Leght, Text = 1):
		ly = self.h - (Value / self.max) * (self.h - self.Border * 2) - self.Border
		self.Box.create_line(self.w - 1, ly, self.w + Leght, ly, fill = 'black', width = 2)
		self.Box.create_line(2, ly, self.w - 2, ly, fill = '#cacfca', width = 2, dash = 2)
		if Text:
			Str = str(Value) + '%'
			self.Box.create_text(self.w + Leght + len(Str) * 5 + 4, ly, font = "Verdana 12", justify = CENTER, fill = 'black', text = Str)

	def update_data(self):
		for i in range(len(self.Colors)):
			Name = self.ComboboxArray[i].get()
			Index = self.ComboboxArray[i].current()
			
			if Name != '---':
				if len(self.GraphArrays[i]) >= self.w - self.Border * 2:
					self.GraphArrays[i].pop(0)
				TCUValue = self.Uart.TCU[Name]
				if Name == 'DrumRPMDelta':
					TCUValue += GraphNames[Index][1] / 2
				CurrentY = round(TCUValue / GraphNames[Index][1] * (self.h - self.Border * 2))
				self.GraphArrays[i].append(CurrentY)
				
	def update(self):
		self.Box.delete("all")
		self.Box.create_rectangle(1, 1, self.w - 2, self.h - 2, width = 2, fill = '#fafffd')
		
		self.print_line(0, 6, 1)
		self.print_line(self.max * 1 // 4, 6, 1)
		self.print_line(self.max * 1 // 2, 6, 1)
		self.print_line(self.max * 3 // 4, 6, 1)
		self.print_line(self.max * 1 // 1, 6, 1)

		Scale = int(self.ScaleBox.get())

		Count = self.w - self.Border * 2
		Add = Count - Count // Scale
		
		Lx = self.w - self.Border

		while Lx > self.Border:
			self.Box.create_line(Lx, self.h, Lx, self.h - 5, fill = 'black', width = 2)
			Lx -= 6 * Scale

		for i in range(len(self.Colors)):
			Name = self.ComboboxArray[i].get()
			if Name != '---':

				#for lx, ly in enumerate(self.GraphArrays[i]):
				
				for lx in range(len(self.GraphArrays[i]) // Scale):
					if lx > 0:
						x1 = lx * Scale + self.Border - 1 * Scale
						y1 = self.h - self.GraphArrays[i][lx - 1 + Add] - self.Border
						x2 = lx * Scale + self.Border
						y2 = self.h - self.GraphArrays[i][lx + Add] - self.Border
						self.Box.create_line(x1, y1, x2, y2, fill = self.Colors[i], width = 2)

				x = self.w - 20
				y = self.h - self.GraphArrays[i][-1] - 20
				
				y = y // 2
				y = y * 2
				
				self.Box.create_text(x, y, font = "Verdana 10", justify = CENTER, fill = self.Colors[i], text = str(self.Uart.TCU[Name]))

# Светофор.
class _LightIndicator:
	def __init__(self, root, Name, x, y, Color):
		self.x = x
		self.y = y
		self.w = 70
		self.h = 70
		self.Name = Name
		self.OffColor = "#d0d0d0"
		self.OnColor = Color

		# Холст.
		self.Box = Canvas(root, width = self.w, height = self.h, bg = self.OffColor, bd = 0, highlightthickness = 0, relief = 'ridge')
		self.Box.place(x = self.x, y = self.y)
		# Круг
		self.Box.create_oval (0, 0, self.w - 1, self.h - 1, width = 2)
		self.Oval = self.Box.create_oval (5, 5, self.w - 6, self.h - 6, width = 2, fill = "#c0c0c0")
		# Название.
		self.Box.create_text(self.w / 2, self.h // 2, font = "Verdana 16 bold", justify = CENTER, fill = 'black', text = self.Name)
	def update(self, Value):
		if Value > 0:
			self.Box.itemconfig(self.Oval, fill = self.OnColor)
		else:
			self.Box.itemconfig(self.Oval, fill = self.OffColor)

# Индикатор состояния адаптации.
class _AdaptationIndicator:
	def __init__(self, root, x, y):
		self.x = x
		self.y = y
		self.w = 30
		self.h = 70
		self.OffColor = "gray"
		self.OnColor = '#ff4500'

		self.Indicators = {}

		# Холст.
		self.Box = Canvas(root, width = self.w + 3, height = self.h, bg = BackGroundColor, bd = 0, highlightthickness = 0, relief = 'ridge')
		self.Box.place(x = self.x, y = self.y)

		self.Indicators['Up'] = self.draw_triangle(0, self.w,  0)
		self.Indicators['Down'] = self.draw_triangle(self.h - self.w, self.w, 1)

	def draw_triangle(self, y, w, flip):
		Points = [w / 2, y, 0, y + w, w, y + w]
		if flip:
			Points = [0, y, w / 2, y +w, w, y]

		Triangle = self.Box.create_polygon(Points, fill = self.OffColor, outline = 'black', width = 2)
		return Triangle

	def update(self, Value):
		if Value > 0:
			self.Box.itemconfig(self.Indicators['Up'], fill = self.OnColor)
			self.Box.itemconfig(self.Indicators['Down'], fill = self.OffColor)
		elif Value < 0:
			self.Box.itemconfig(self.Indicators['Up'], fill = self.OffColor)
			self.Box.itemconfig(self.Indicators['Down'], fill = self.OnColor)
		else:
			self.Box.itemconfig(self.Indicators['Up'], fill = self.OffColor)
			self.Box.itemconfig(self.Indicators['Down'], fill = self.OffColor)