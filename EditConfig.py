from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
import tkinter as tk
import time

import ToolTip
import Tables

BackGroundColor = "#d0d0d0"

ConfigComments = {'AfterChangeMinRPM' : 	'Если обороты после переключения будут ниже этого значения, то переключение блокируется.'
				, 'AfterChangeMaxRPM' :		'Если обороты после переключения будут выше этого значения, то переключение блокируется.'

				, 'IdleTPSLimit' :			'Положение ДПДЗ до этого значения считается как ХХ. Точное определение ХХ необходимо для правильной работы второй передачи.'
				, 'MaxSlipRPM' :			'Разница в оборотах валов для обнаружения проскальзывания.'
				, 'RearGearInitMaxSpeed' :	'Задняя передача не включится, если скорость превышает этот порог.'
				, 'PowerDownMaxTPS' :		'При ДПДЗ выше этого порога не будет посылаться запрос снижения мощности.'

				, 'MinPressureSLN' :	'ШИМ для минимального давления SLN подпора гидроаккумуляторов.'
				, 'IdlePressureSLN' :	'ШИМ простоя (максимальное давление подпора гидроаккумуляторов).'
				, 'MinPressureSLU' :	'ШИМ для минимального давления SLU.'

				, 'GlockStartValue' :	'Значение ШИМ, при котором начинает работать блокировка ГТ на прогретом двигателе.'
				, 'GlockWorkValue' :	'Рабочее значение ШИМ блокировки гидротрансформатора.'
				, 'GlockMaxTPS' :		'Значение ДПДЗ, выше которого блокировка ГТ отключается.'

				, 'AdaptationStepRatio' : 'При быстрой адаптации удваивается шаг смещения точки, что увеличивает скорость, но снижает точность работа алгоритма. Включать только при первоначальной настройке таблиц.'

				, 'G2EnableAdaptTPS' :	'Включение алгоритма адаптации давления SLU по ДПДЗ. Алгоритм работает в диапазоне температур, указанных ниже (>=, <=). Сначала надо откатать по ДПДЗ на прогретом масле и при отключенной адаптации по температуре.'
				, 'G2AdaptTPSTempMin' :	'При температуре масла ниже этого порога адаптация по ДПДЗ отключается, и включается адаптация по температуре масла.'
				, 'G2AdaptTPSTempMax' :	'При температуре масла выше этого порога адаптация по ДПДЗ отключается, и включается адаптация по температуре масла.'
				, 'G2EnableAdaptTemp' :	'Включение алгоритма адаптации коррекции давления SLU по температуре, алгоритм работает вне диапазоне температур для ДПДЗ, указанных выше. Включать только после успешной настройки графика давления SLU второй передачи от ДПДЗ.'
				, 'G2AdaptTempMaxTPS' :	'Порог ДПДЗ для отключения алгоритма адаптации коррекции давления SLU по температуре.'

				, 'G2EnableAdaptReact' :	'Включение алгоритма адаптации опережения по оборотам реактивации второй передачи. Алгоритм работает в диапазоне температур, указанных ниже (>=, <=). Сначала надо откатать этот график на прогретом масле и при отключенной адаптации по температуре.'
				, 'G2AdaptReactMinDRPM' :	'При ускорении первичного вала ниже этого порога адаптация не работает.'
				, 'G2AdaptReactTempMin' :	'При температуре масла ниже этого порога адаптация по ускорению отключается, и включается адаптация по температуре масла.'
				, 'G2AdaptReactTempMax' :	'При температуре масла выше этого порога адаптация по ускорению отключается, и включается адаптация по температуре масла.'
				, 'G2EnableAdaptRctTemp' :	'Включение алгоритма адаптации коррекции опережения по температуре, алгоритм работает вне диапазоне температур для ускорения, указанных выше. Включать только после успешной настройки графика опережение по оборотам реактивации второй передачи.'
				, 'G2AdaptRctTempMaxTPS' :	'Порог ДПДЗ для отключения алгоритма адаптации коррекции опережения по оборотам реактивации второй передачи.'
				, 'G2ReactStepSize' :		'Длительность 1 шага при реактивации второй передачи.'

				, 'G3EnableAdaptTPS' :	'Включение алгоритма адаптации времени удержания SLU по ДПДЗ. Алгоритм работает в диапазоне температур, указанных ниже (>=, <=). Сначала надо откатать по ДПДЗ на прогретом масле и при отключенной адаптации по температуре.'
				, 'G3AdaptTPSTempMin' :	'При температуре масла ниже этого порога адаптация по ДПДЗ отключается, и включается адаптация по температуре масла.'
				, 'G3AdaptTPSTempMax' :	'При температуре масла выше этого порога адаптация по ДПДЗ отключается, и включается адаптация по температуре масла.'
				, 'G3EnableAdaptTemp' :	'Включение алгоритма адаптации коррекции времени удержания SLU по температуре, алгоритм работает вне диапазоне температур для ДПДЗ, указанных выше. Включать только после успешной настройки графика давления SLU второй передачи от ДПДЗ.'
				, 'G3AdaptTempMaxTPS' :	'Порог ДПДЗ для отключения алгоритма адаптации коррекции давления SLU по температуре.'

				, 'SpeedImpulsPerKM' :	'Количество импульсов на 1 км для генерации сигнала на спидометр'
				, 'SpeedCalcCoef' :		'Коэффициент для перевода оборотов выходного вала в скорость. Вычисляется по формуле (1 / [Передаточное число гравной пары]) * [Длина окружности колеса] * 60 * 4.096. Округряем до ближайщего целого и записываем сюда. Для ВАЗ 2104, к примеру, коффициент получается - 114.'

				, 'BaroCorrEnable' :		'Барокоррекция смещает текущую нагрузку в зависимости от атмосферного давления. Например, в горах атмосферное давление ниже, поэтому при том же значении ДПДЗ крутящий момент будет меньше.'
				, 'DefaultBaroPressure' :	'Стандартное атмосферное давление в кПа, отностительно которого будет производиться коррекция.'

				, 'TiptronicEnable' :		'Включение ручного режима АКПП (Типтроник). При нажатии кнопки переключения АКПП перейдёт в ручной режим, который будет активен указанное время или до переключения селектора.'
				, 'TiptronicTimer' :		'Время работы ручного режима (1 шаг = 100мс), по истечении этого времени АКПП вернётся в обычный режим. При каждом нажатии кнопки таймер сбрасывается.'
}

# Окно редактирования настроек.
class _ConfigEditWindow:
	def __init__(self, Uart):
		self.root = tk.Toplevel()
		self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.WindowOpen = 1
		self.WindowName = 'EditConfig'

		self.Uart = Uart

		self.Width = 1180
		self.Height = 650
		self.OffsetX = 20
		self.OffsetY = 0

		self.CellColor = "#d0ddd0"

		self.MainFont = font.Font(size = 10)
		self.root.option_add("*Font", self.MainFont)
		self.root.title('Редакирование настроек')
		self.root.minsize(self.Width, self.Height)
		self.root.configure(background = BackGroundColor)

		# Чтение/Запись
		self.ReadBtn = Button(self.root, text = "Считать", width = 8, bg = "#4caa00", command = self.get_config, font = ("Helvetica", 12, 'bold'))
		self.ReadBtn.place(x = 80, y = 8)
		self.WriteBtn = Button(self.root, text = "Записать", width = 8, bg = "#cd5500", command = self.write_config, font = ("Helvetica", 12, 'bold'), state = 'disabled')
		self.WriteBtn.place(x = 80, y = 45)

		# Индикатор ответа ЭБУ.
		self.Answer = _LightIndicator(self.root, 'A', 200, 28)

		self.EReadBtn = Button(self.root, text = "Считать из EEPROM", width = 19, bg = "#adff2f", command = self.read_eeprom, font = ("Helvetica", 12, 'bold'))
		self.EReadBtn.place(x = 300, y = 8)
		self.ESaveBtn = Button(self.root, text = "Сохранить в EEPROM", width = 19, bg = "#ff8c00", command = self.write_eeprom, font = ("Helvetica", 12, 'bold'))
		self.ESaveBtn.place(x = 300, y = 45)

		# Экспорт / Импорт.
		self.ExportBtn = Button(self.root, text = "Экспорт", width = 8, bg = "#6495ed", command = self.to_excel, font = ("Helvetica", 12, 'bold'))
		self.ExportBtn.place(x = 550, y = 8)
		self.ImportBtn = Button(self.root, text = "Импорт", width = 8, bg = "#bc8f8f", command = self.from_excel, font = ("Helvetica", 12, 'bold'))
		self.ImportBtn.place(x = 550, y = 45)

		# Сброс таблиц.
		self.TableResetBtn = Button(self.root, text = "Сброс\nнастроек", width = 8, bg = "#B44444", command = self.reset_config, font = ("Helvetica", 12, 'bold'))
		self.TableResetBtn.place(x = 780, y = 8)

		# Выход.
		self.ExitBtn = Button(self.root, text = "Закрыть", width = 12, height = 3, bg = "#cd853f", command = self.on_closing, font = ("Helvetica", 12, 'bold'))
		self.ExitBtn.place(x = 990, y = 8)

		# Рисуем блоки с параметрами.
		self.draw_config_elements()
		# Добавляем подсказки.
		self.add_tooltip()
		# Запрашиваем конфигурацию.
		self.get_config()

	def add_parameter(self, X, Y, W, Name):
		Label = ttk.Label(self.root, text = Tables.ConfigData[Name]['Name'], relief = 'flat', font = self.MainFont, background = self.MainBG, padding = 3, wraplength = W - 60)
		Label.place(x = X, y = Y)

		LH = Label.winfo_reqheight()

		Tables.ConfigData[Name]['Value'] = IntVar(value = 0)
		Type = Tables.ConfigData[Name]['Element']
		MaxLen = 4

		if Type == 'Entry':
			Element = Entry(self.root
							, textvariable = Tables.ConfigData[Name]['Value']
							, justify = 'center'
							, bg = self.CellColor
							, width = MaxLen
							, font = ("Helvetica", 14))

			Add = (LH - Element.winfo_reqheight()) / 2
			Element.place(x = W + 10, y = Y + Add, anchor = 'ne')
		elif Type == 'Spinbox':
			Element = Spinbox(self.root
							, textvariable = Tables.ConfigData[Name]['Value']
							, justify = 'center'
							, bg = self.CellColor
							, width = MaxLen
							, font = ("Helvetica", 14)
							, from_ = Tables.ConfigData[Name]['Min']
							, to = Tables.ConfigData[Name]['Max']
							, increment = Tables.ConfigData[Name]['Step'])
			Add = (LH - Element.winfo_reqheight()) / 2
			Element.place(x = X + W, y = Y + Add, anchor = 'ne')			
		if Type == 'CheckButton':
			Element = Checkbutton(self.root
							, text = ''
							, variable = Tables.ConfigData[Name]['Value']
							, onvalue = Tables.ConfigData[Name]['Max']
							, offvalue = Tables.ConfigData[Name]['Min']
							, background = BackGroundColor)

			Add = (LH - Element.winfo_reqheight()) / 2
			Element.place(x = X + W, y = Y + Add, anchor = 'ne')

		ToolTip.ToolTip(Element, ConfigComments[Name])
		Element.bind("<FocusOut>", self.value_check)

		return LH

	def add_block(self, X, Y, W, Name, Block):
		Border = ttk.Label(self.root, text = '', relief = "ridge", background = BackGroundColor)
		Border.place(x = X - 5, y = Y - 5, width = 10, height = 10)

		Label = ttk.Label(self.root, text = Name, relief = "groove", font = self.СapitalFont, background = self.CapitalBG, wraplength = W - 10, padding = 3, justify = 'center', anchor = 'center')
		Label.place(x = X, y = Y, width = W)

		H = Label.winfo_reqheight()

		N = 0
		LastY = Y + H + 7
		LastH = 0
		for Key in Tables.ConfigData:
			if Tables.ConfigData[Key]['Block'] == Block:
				LastY += LastH
				LastH = self.add_parameter(X, LastY, W, Key)
				N += 1

		Border.place(width = W + 10, height = LastY + LastH - Y + 10)
		return LastY + LastH - Y + 10

	def draw_config_elements(self):
		self.СapitalFont = ('Helvetica bold', 12)
		self.CapitalBG = '#8899AA'
		self.CapitalLength = 377
		self.MainFont = ('Helvetica bold', 12)
		self.MainBG = BackGroundColor
		self.MaintLength = self.CapitalLength - 50

		BorderY = 120
		# Столбец № 1.
		StartY = 0
		StartY += self.add_block(10, StartY + BorderY, self.CapitalLength, 'Пороги / ограничения', 1)
		StartY += self.add_block(10, StartY + BorderY, self.CapitalLength, 'ШИМ соленоидов', 2)
		StartY += self.add_block(10, StartY + BorderY, self.CapitalLength, 'Блокировка ГТ', 3)
		StartY += self.add_block(10, StartY + BorderY, self.CapitalLength, 'Барокоррекция', 9)

		# Столбец № 2.
		StartY = 0
		StartY += self.add_block(10 + (self.CapitalLength + 15) * 1, StartY + BorderY, self.CapitalLength, 'Адаптация, общие настройки', 4)
		StartY += self.add_block(10 + (self.CapitalLength + 15) * 1, StartY + BorderY, self.CapitalLength, 'Адаптация SLU второй передачи', 5)
		StartY += self.add_block(10 + (self.CapitalLength + 15) * 1, StartY + BorderY, self.CapitalLength, 'Адаптация реактивации второй передачи', 6)

		# Столбец № 2.
		StartY = 0
		StartY += self.add_block(10 + (self.CapitalLength + 15) * 2, StartY + BorderY, self.CapitalLength, 'Адаптация времени удержания SLU третьей передачи', 7)
		StartY += self.add_block(10 + (self.CapitalLength + 15) * 2, StartY + BorderY, self.CapitalLength, 'Расчёт скорости', 8)
		StartY += self.add_block(10 + (self.CapitalLength + 15) * 2, StartY + BorderY, self.CapitalLength, 'Ограничения по оборотам при переключении', 0)
		StartY += self.add_block(10 + (self.CapitalLength + 15) * 2, StartY + BorderY, self.CapitalLength, 'Типтроник', 10)

	def value_check(self, event):	# Проверка и исправление значений.
		for Key in Tables.ConfigData:
			Value = 0
			try:
				Value = int(Tables.ConfigData[Key]['Value'].get())
			except:
				Tables.ConfigData[Key]['Value'].set(0)
			else:
				if Value < Tables.ConfigData[Key]['Min']:
					Tables.ConfigData[Key]['Value'].set(Tables.ConfigData[Key]['Min']) 
				elif Value > Tables.ConfigData[Key]['Max']:
					Tables.ConfigData[Key]['Value'].set(Tables.ConfigData[Key]['Max']) 

	def add_tooltip(self):	# Вставка подсказок.
		ToolTip.ToolTip(self.ReadBtn, "Считать настройки из оперативной памяти ЭБУ")
		ToolTip.ToolTip(self.WriteBtn, "Отправить настройки в ЭБУ. Настройки будут записаны в ОЗУ, для сохранения изменений необходимо сохаанить в EEPROM.")
		
		ToolTip.ToolTip(self.Answer.Box, "Индикатор ответа ЭБУ на команду. Красный - команда не принята. Зелёный - команда успешно обработана.")

		ToolTip.ToolTip(self.EReadBtn, "Считать все настройки из EEPROM в ОЗУ")
		ToolTip.ToolTip(self.ESaveBtn, "Сохранить все настройки из ОЗУ в EEPROM")

		ToolTip.ToolTip(self.ExportBtn, "Экспорт настроек в буфер обмена.")
		ToolTip.ToolTip(self.ImportBtn, "Импорт настроек из буфер обмена.")

		ToolTip.ToolTip(self.TableResetBtn, "Сброс настроек. Значения заменяются на начальные из прошивки и производтся запись в EEPROM. Можно использовать в том числе для первоначальной записи настроек в EEPROM.")

		ToolTip.ToolTip(self.ExitBtn, "Закрыть окно.")

	def to_excel(self):	# Экспорт данных в Excel.
		if self.value_check(''):
			pass

	def from_excel(self):	# Импорт данных из Excel.
		Buffer = self.root.clipboard_get().split('\t')
		for Key in Tables.ConfigData:
			pass

	def read_config(self):	# Событие при получении данных из ЭБУ.
		for Key in Tables.ConfigData:
			Tables.ConfigData[Key]['Value'].set(self.Uart.CFG[Key])
		self.Answer.update(0)
		self.WriteBtn.config(state='normal')

	def get_config(self):	# Команда на получение настроек из ЭБУ.
		self.Answer.update(1)
		self.Uart.send_command('GET_CONFIG_COMMAND', 0, [], self.root)

	def write_config(self):	# Команда на запись таблицы в ОЗУ ЭБУ.
		self.Answer.update(1)
		self.Uart.send_command('NEW_CONFIG_DATA', 0, [], self.root)

	def read_eeprom(self):	# Команда на чтение EEPROM.
		self.Answer.update(1)
		self.Uart.send_command('READ_EEPROM_CONFIG_COMMAND', 0, [], self.root)

	def write_eeprom(self):	# Команда на запись EEPROM.
		self.Answer.update(1)
		self.Uart.send_command('WRITE_EEPROM_CONFIG_COMMAND', 0, [], self.root)
	
	def reset_config(self):	# Команда сброса таблиц в ЭБУ.
		if messagebox.askyesno('Сброс таблиц', 'Перезаписать EEPROM ВСЕX таблицы текущего окна значениями из прошивки?', parent = self.root):
			time.sleep(0.5)
			self.Answer.update(1)
			self.Uart.send_command('TABLES_INIT_CONFIG_COMMAND', 0, [], self.root)

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