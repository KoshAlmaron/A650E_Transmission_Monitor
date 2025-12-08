from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
import tkinter as tk
import time
from functools import partial


import ToolTip
import Tables

BackGroundColor = "#d0d0d0"

LabelsTCU = [['Inst TPS', 'InstTPS', ' Текущее значение ДПДЗ.'],
			 ['TPS', 'GearChangeTPS', ' ДПДЗ на момент последнего переключения.'],
			 ['G2 LastStep', 'LastStep', ' Номер последнего шага включения второй передачи.'],
			 ['SLT', 'GearChangeSLT', ' Значение SLT на момент последнего переключения.'],
			 ['SLN', 'GearChangeSLN', ' Значение SLN на момент последнего переключения.'],
			 ['SLU', 'GearChangeSLU', ' Значение SLU на момент последнего переключения.'],
			 ['PDRTime', 'LastPDRTime', ' Продолжительность последнего запроса снижения мощности.'],
			]

TablesMenuNames = {0: 'Общие графики SLN/SLT'
				, 1: 'Графики переключения 1>2'
				, 2: 'Графики переключения 2>2'
				, 3: 'Графики переключения 2>3'
}

FirstTable = 0
LastTable = 17

# Окно редактирования таблиц.
class _TableEditWindow:
	def __init__(self, Uart):
		self.root = tk.Toplevel()
		self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.WindowOpen = 1
		self.WindowName = 'EditTables'

		self.Uart = Uart
		self.Cells = []
		self.Labels = []
		self.DataTCU = {}

		self.GetNewTable = 0
		self.CurrentTable = FirstTable

		self.Width = 1180
		self.Height = 680
		self.OffsetX = 20
		self.OffsetY = 0

		self.CellColor = "#d0ddd0"
		self.ErrorColor = "#e0a0a0"

		self.MainFont = font.Font(size = 10)
		self.root.option_add("*Font", self.MainFont)
		self.root.title('Редакирование таблиц')
		self.root.minsize(self.Width, self.Height)
		self.root.configure(background = BackGroundColor)

		# Галка "Онлайн".
		self.OnLine = IntVar()
		self.OnLineChk = Checkbutton(self.root, text='Онлайн', variable = self.OnLine, onvalue = 1, offvalue = 0, background = BackGroundColor, font = ("Helvetica", 14, 'bold'))
		self.OnLineChk.place(x = 25, y = 11)

		# Галка "Автообновление".
		self.AutoUpdate = IntVar()
		self.AutoUpdateChk = Checkbutton(self.root, text='Автообн.', variable = self.AutoUpdate, command = self.command_buttons_disable, onvalue = 1, offvalue = 0, background = BackGroundColor, font = ("Helvetica", 14, 'bold'), state = 'disabled')
		self.AutoUpdateChk.place(x = 25, y = 48)

		# Чтение/Запись
		self.ReadBtn = Button(self.root, text = "Считать", width = 8, bg = "#4caa00", command = self.get_table, font = ("Helvetica", 12, 'bold'))
		self.ReadBtn.place(x = 150, y = 8)
		self.WriteBtn = Button(self.root, text = "Записать", width = 8, bg = "#cd5500", command = self.write_table, font = ("Helvetica", 12, 'bold'), state = 'disabled')
		self.WriteBtn.place(x = 150, y = 45)

		# Индикатор ответа ЭБУ.
		self.Answer = _LightIndicator(self.root, 'A', 263, 28)

		self.EReadBtn = Button(self.root, text = "Считать из EEPROM", width = 19, bg = "#adff2f", command = self.read_eeprom, font = ("Helvetica", 12, 'bold'))
		self.EReadBtn.place(x = 310, y = 8)
		self.ESaveBtn = Button(self.root, text = "Сохранить в EEPROM", width = 19, bg = "#ff8c00", command = self.write_eeprom, font = ("Helvetica", 12, 'bold'))
		self.ESaveBtn.place(x = 310, y = 45)

		# Экспорт / Импорт.
		self.ExportBtn = Button(self.root, text = "Экспорт", width = 8, bg = "#6495ed", command = self.to_excel, font = ("Helvetica", 12, 'bold'))
		self.ExportBtn.place(x = 550, y = 8)
		self.ImportBtn = Button(self.root, text = "Импорт", width = 8, bg = "#bc8f8f", command = self.from_excel, font = ("Helvetica", 12, 'bold'))
		self.ImportBtn.place(x = 550, y = 45)

		# Ограничения переключения передач.
		self.MinGearBox = ttk.Combobox(self.root, values = (1, 2, 3, 4, 5), state = "readonly", width = 2, font = ("Helvetica", 16))
		self.MinGearBox.place(x = 695, y = 10)
		self.MinGearBox.current(0)
		self.MinGearBox.bind("<<ComboboxSelected>>", self.min_gear_selected_event)
		self.MaxGearBox = ttk.Combobox(self.root, values = (1, 2, 3, 4, 5), state = "readonly", width = 2, font = ("Helvetica", 16))
		self.MaxGearBox.place(x = 770, y = 10)
		self.MaxGearBox.current(4)
		self.MaxGearBox.bind("<<ComboboxSelected>>", self.max_gear_selected_event)
		self.GearSetLimitBtn = Button(self.root, text = "Установить", width = 10, bg = "#b0c4de", command = self.set_gear_limit, font = ("Helvetica", 12, 'bold'))
		self.GearSetLimitBtn.place(x = 695, y = 45)

		# Сброс таблиц.
		self.TableResetBtn = Button(self.root, text = "Сброс\nтаблиц", width = 8, bg = "#B44444", command = self.reset_tables, font = ("Helvetica", 12, 'bold'))
		self.TableResetBtn.place(x = 850, y = 8)

		# Выход.
		self.ExitBtn = Button(self.root, text = "Закрыть", width = 12, height = 3, bg = "#cd853f", command = self.on_closing, font = ("Helvetica", 12, 'bold'))
		self.ExitBtn.place(x = 990, y = 8)

		# Добавление пунктов меню.
		self.add_menu()

		# Название текущей таблицы.
		self.TableName = ttk.Label(self.root, text = '', width = 106, anchor = CENTER, relief = "flat", background = BackGroundColor, font = ("Helvetica", 14))
		self.TableName.place(x = 35, y = 155)

		# График.
		self.MainGraph = _Graph(self.root, 35, 190, Uart)
		self.draw_table()
		self.MainGraph.redraw(self.CurrentTable, self.get_array_x())
		if self.Uart.port_status():
			self.get_table()
		self.MainGraph.update_data(self.Cells, 0)

		# Значения TCU Data
		self.draw_labels(37, 87)

		self.draw_graph_buttons(190 + 400 / 2)

		self.add_tooltip()

		self.table_select_event(FirstTable)

		# Обнаружение нажатия кнопок.
		self.root.bind("<Key>", self.key_pressed)

	def add_tooltip(self):	# Вставка подсказок.
		ToolTip.ToolTip(self.OnLineChk, "Онлайн режим. Изменения сразу отсылаются в ЭБУ.")
		ToolTip.ToolTip(self.AutoUpdateChk, "Автообновление таблицы. Период - 1с, доступно только для таблиц адаптации.")
		
		ToolTip.ToolTip(self.ReadBtn, "Считать таблицу из оперативной памяти ЭБУ")
		ToolTip.ToolTip(self.WriteBtn, "Отправить таблицу в ЭБУ. Таблица будет записана в ОЗУ, для сохранения изменений необходимо перенести таблицу в EEPROM.")
		
		ToolTip.ToolTip(self.Answer.Box, "Индикатор ответа ЭБУ на команду. Красный - команда не принята. Зелёный - команда успешно обработана.")

		ToolTip.ToolTip(self.EReadBtn, "Считать все таблицы из EEPROM в ОЗУ")
		ToolTip.ToolTip(self.ESaveBtn, "Сохранить все таблицы из ОЗУ в EEPROM")

		ToolTip.ToolTip(self.ExportBtn, "Экспорт текущей таблицы в буфер обмена. Значения передаюся в буфер с разделителем-табуляцией для дальнейшей вставки в Excel.")
		ToolTip.ToolTip(self.ImportBtn, "Импорт таблицы из буфер обмена. Значения должны быть с разделителем-табуляцией и в таком же количестве.")
		
		ToolTip.ToolTip(self.MinGearBox, "Минимальная допустимая передача. Используется для настройки переключений.")
		ToolTip.ToolTip(self.MaxGearBox, "Максимальная допустимая передача. Используется для настройки переключений.")
		ToolTip.ToolTip(self.GearSetLimitBtn, "Установить ограничения по передачам в ЭБУ")

		ToolTip.ToolTip(self.TableResetBtn, "Сброс всех таблиц текущего окна. Значения заменяются на начальные из прошивки и производтся запись в EEPROM. Можно использовать в том числе для первоначальной записи таблиц в EEPROM.")
		ToolTip.ToolTip(self.ExitBtn, "Закрыть окно.")

		ToolTip.ToolTip(self.BtnBuildLine, "Построить линию по двум точкам")
		ToolTip.ToolTip(self.BtnZero, "Обнуление графика")
		ToolTip.ToolTip(self.BtnApplyAdapt, "Применение адаптации к текущей таблице. После применения таблица адаптации обнуляется. Все изменения производятся в ОЗУ ЭБУ, для сохранения изменений необходимо произвести запись в EEPROM.")

	def add_menu(self):
		self.root.option_add("*tearOff", FALSE)
		MenuBGColor = "#a0a0a0"
		self.MainMenu = Menu(font = ("Helvetica", 12, 'bold'), background = MenuBGColor)
		MenuFont = ("Helvetica", 12)

		SubMenu = None
		for Key in TablesMenuNames:
			SubMenu = Menu(font = MenuFont)
			K = 1
			for Table in Tables.TablesData:
				if Table['Menu'] == Key:
					N = Table['N']
					LabelName = str(Key + 1) + '.' + str(K) + '. ' + Table['Name']
					LabelName = str(K) + '. ' + Table['Name']
					SubMenu.add_command(label = LabelName, command = partial(self.table_select_event, N))
					K += 1

			self.MainMenu.add_cascade(label = str(Key + 1) + '. ' + TablesMenuNames[Key], menu = SubMenu)
			SubMenu = None

		self.root.config(menu = self.MainMenu)

	def apply_adaptation(self): # Применение адаптации к текущему графику.
		Number = self.CurrentTable
		Name = Tables.TablesData[Number]['Table']

		if Name in Tables.ApplyAdaptationCommands:
			self.Answer.update(1)
			Command = Tables.ApplyAdaptationCommands[Name]
			self.Uart.send_command(Command, Number, [])

	def build_line(self):
		Start = self.MainGraph.CursorPositionL
		Stop = self.MainGraph.CursorPositionR
		if Start == Stop:
			Start = 0
			Stop = len(self.Cells) - 1

		ArrayLen = len(self.Cells) - 1

		ArrayLen = Stop - Start
		Min = int(self.Cells[Start].get())
		Max = int(self.Cells[Stop].get())
		Step = (Max - Min) / ArrayLen

		for i in range(0, ArrayLen + 1):
			self.Cells[Start + i].delete(0, END)
			Value = round(Min + Step * i)
			self.Cells[Start + i].insert(0, str(Value))

		self.value_check('')

	def reset_tables(self):	# Команда сброса таблиц в ЭБУ.
		if messagebox.askyesno('Сброс таблиц', 'Перезаписать EEPROM ВСЕX таблицы текущего окна значениями из прошивки?'):
			self.table_select_event(FirstTable)
			self.root.lift()

			time.sleep(0.5)
			self.Answer.update(1)
			self.Uart.send_command('TABLES_INIT_MAIN_COMMAND', self.CurrentTable, [])
		else:
			self.root.lift()

	def set_gear_limit(self):	# Команда установки ограничения передач.
		MinGear = int(self.MinGearBox.get())
		MaxGear = int(self.MaxGearBox.get())

		self.Answer.update(1)
		self.Uart.send_command('GEAR_LIMIT_COMMAND', self.CurrentTable, [MinGear, MaxGear])

	def min_gear_selected_event(self, event):	# Событие смены ограничения передачи (min).
		if self.MaxGearBox.current() < self.MinGearBox.current():
			self.MaxGearBox.current(self.MinGearBox.current())

	def max_gear_selected_event(self, event):	# Событие смены ограничения передачи (max).
		if self.MinGearBox.current() > self.MaxGearBox.current():
			self.MinGearBox.current(self.MaxGearBox.current())

	def draw_graph_buttons(self, Y):	# Отрисовка кнопок на графике.
		X = 5
		H = 13

		self.BtnBuildLine = Button(self.root, text = "L", width = 1, bg = "#bcbcbc", command = self.build_line, font = ("Helvetica", 10, 'bold'), border="2px", state = 'normal')
		self.BtnBuildLine.place(x = X, y = Y - H - 95, width = 25, height = 25)

		self.BtnApplyAdapt = Button(self.root, text = "A", width = 1, bg = "#bcbcbc", command = self.apply_adaptation, font = ("Helvetica", 10, 'bold'), border="2px", state = 'disabled')
		self.BtnApplyAdapt.place(x = X, y = Y - H - 150, width = 25, height = 25)

		self.BtnZero = Button(self.root, text = "0", width = 1, bg = "#bcbcbc", command = lambda: self.move_graph(0), font = ("Helvetica", 10, 'bold'), border="2px")
		self.BtnZero.place(x = X, y = Y - H, width = 25, height = 25)

		Button(self.root, text = "+", width = 1, bg = "#bcbcbc", command = lambda: self.move_graph(1), font = ("Helvetica", 10, 'bold'), border="2px").place(x = X, y = Y - H - 40, width = 25, height = 25)
		Button(self.root, text = "-", width = 1, bg = "#bcbcbc", command = lambda: self.move_graph(-1), font = ("Helvetica", 10, 'bold'), border="2px").place(x = X, y = Y - H + 40, width = 25, height = 25)

	def move_graph(self, Where):	# Перемещение точек на графике.
		N = self.CurrentTable
		Step = Tables.TablesData[N]['Step']
		for Cell in self.Cells:
			Value = int(Cell.get())
			if Where == 0:
				Value = 0
			elif Where == 1:
				Value += Step
			elif Where == -1:
				Value -= Step
			Cell.delete(0, END)
			Cell.insert(0, str(Value))

		self.value_check('')
		if self.OnLine.get() == 1:
			self.write_table()		

	def to_excel(self):	# Экспорт данных в Excel.
		if self.value_check(''):
			Buffer = ''
			for Cell in self.Cells:
				Buffer += Cell.get() + '\t'

			self.root.clipboard_clear()
			self.root.clipboard_append(Buffer[:-1])				

	def from_excel(self):	# Импорт данных из Excel.
		Buffer = self.root.clipboard_get().split('\t')
		if len(Buffer) == len(self.get_array_x()):
			for N, Cell in enumerate(self.Cells):
				Cell.delete(0, END)
				Cell.insert(0, str(Buffer[N]))
			self.value_check('')

	def get_array_x(self):	# Получить сетку по оси X.
		return Tables.TablesData[self.CurrentTable]['ArrayX']

	def key_pressed(self, event):	# Событие по нажатию кнопки на клавиатуре.
		Result = self.MainGraph.move_point(event.keysym, event.state, self.Cells)
		if Result:
			self.value_check('')
			if self.OnLine.get() == 1 and Result == 2:
				self.write_table()

	def table_auto_update(self):
		if self.AutoUpdate.get() == 1:
			if Tables.TablesData[self.CurrentTable]['Name'][:4] == '    ':
				self.get_table()

	def command_buttons_disable(self):
		if self.AutoUpdate.get() == 1:
			self.OnLineChk.configure(state = 'disabled')
			self.OnLine.set(0)

			self.ReadBtn.configure(state = 'disabled')
			self.WriteBtn.configure(state = 'disabled')
			self.EReadBtn.configure(state = 'disabled')
			self.ESaveBtn.configure(state = 'disabled')
			self.GearSetLimitBtn.configure(state = 'disabled')
			self.TableResetBtn.configure(state = 'disabled')

		else:
			self.OnLineChk.configure(state = 'normal')
			self.ReadBtn.configure(state = 'normal')
			self.WriteBtn.configure(state = 'normal')
			self.EReadBtn.configure(state = 'normal')
			self.ESaveBtn.configure(state = 'normal')
			self.GearSetLimitBtn.configure(state = 'normal')
			self.TableResetBtn.configure(state = 'normal')

	def get_table(self):	# Команда на получение таблицы из ЭБУ.
		self.Answer.update(1)
		self.GetNewTable = 1
		self.Uart.send_command('GET_TABLE_COMMAND', self.CurrentTable, [])

	def read_table(self):	# Событие при получении данных из ЭБУ.
		#print('Получена таблица', self.Uart.TableNumber)
		#print(self.Uart.TableNumber, self.CurrentTable)
		#print(len(self.Uart.TableData),  len(self.get_array_x()))
		if self.Uart.TableNumber == self.CurrentTable:
			if len(self.Uart.TableData) == len(self.get_array_x()):
				
				self.WriteBtn.config(state='normal')
				
				CurrGrid = self.get_array_x()
				for i in range(0, len(CurrGrid), 1):
					self.Cells[i].delete(0, END)
					self.Cells[i].insert(0, self.Uart.TableData[i])

				self.MainGraph.update_data(self.Cells, self.GetNewTable)
				self.GetNewTable = 0
				self.Answer.update(0)

	def write_table(self):	# Команда на запись таблицы в ОЗУ ЭБУ.
		self.Answer.update(1)
		Data = []
		for Cell in self.Cells:
			Data.append(int(Cell.get()))
		self.Uart.send_command('NEW_TABLE_DATA', self.CurrentTable, Data)

	def read_eeprom(self):	# Команда на чтение EEPROM.

		self.Answer.update(1)
		self.Uart.send_command('READ_EEPROM_MAIN_COMMAND', self.CurrentTable, [])

	def write_eeprom(self):	# Команда на запись EEPROM.
		self.Answer.update(1)
		self.Uart.send_command('WRITE_EEPROM_MAIN_COMMAND', self.CurrentTable, [])

	def value_check(self, event):	# Проверка и исправление значений таблицы.
		N = self.CurrentTable
		AllIsOk = 1
		for Cell in self.Cells:
			try:
				Value = int(Cell.get())
				if Value < Tables.TablesData[N]['Min']:
					Cell.delete(0, END)
					Cell.insert(0, str(Tables.TablesData[N]['Min']))
				elif Value > Tables.TablesData[N]['Max']:
					Cell.delete(0, END)
					Cell.insert(0, str(Tables.TablesData[N]['Max']))
				else:
					Cell.delete(0, END)
					Cell.insert(0, str(Value))

				Cell.configure(background = self.CellColor)
			except Exception as error:
				Cell.configure(background = self.ErrorColor)
				AllIsOk = 0

		if AllIsOk:
			self.WriteBtn.config(state='normal')
			self.MainGraph.update_data(self.Cells, 0)
			return 1
		else:
			self.WriteBtn.config(state='disabled')
			return 0

	def table_select_event(self, N):	# Событие при выборе текущей таблицы.
		self.CurrentTable = N

		self.TableName.config(text = Tables.TablesData[self.CurrentTable]['Name'])

		self.clear_table()
		self.draw_table()
		self.MainGraph.redraw(self.CurrentTable, self.get_array_x())
		self.MainGraph.update_data(self.Cells, 0)

		self.MainGraph.CursorPositionL = 0
		self.MainGraph.CursorPositionR = 0

		if Tables.TablesData[self.CurrentTable]['Table'] in Tables.ApplyAdaptationCommands:
			self.BtnApplyAdapt.configure(state = 'normal')
		else:
			self.BtnApplyAdapt.configure(state = 'disabled')

		if Tables.TablesData[self.CurrentTable]['Name'][:4] == '    ':
			self.AutoUpdateChk.configure(state = 'normal')
		else:
			self.AutoUpdateChk.configure(state = 'disabled')
			self.AutoUpdate.set(0)

		if self.Uart.port_status():
			self.get_table()

		self.OnLine.set(0)
		self.AutoUpdate.set(0)
		self.command_buttons_disable()

	def clear_table(self):	# Очистка таблицы в интерфейсе.
		for Cell in self.Cells:
			Cell.destroy()
		for Label in self.Labels:
			Label.destroy()
		
		self.Cells = []
		self.Labels = []			

	def draw_table(self):	# Отрисовка таблицы.
		W = 4
		X = 35
		Y = 630
		Space = 52.5
		if self.get_array_x() == Tables.TempGrid:
			Space = 35

		for Col, Value in enumerate(self.get_array_x()):
			Cell = Entry(self.root, justify = "center", bg = self.CellColor, width = W)
			Default = Tables.TablesData[self.CurrentTable]['Min']
			if Default < 0:
				Default = 0

			Cell.insert(0, Default)
			Cell.place(x = X + Space * Col, y = Y)
			Cell.bind("<FocusOut>", self.value_check)
			self.Cells.append(Cell)	

			Label = ttk.Label(self.root, text = Value, width = W, anchor = CENTER, relief = "flat", background = BackGroundColor)
			Label.place(x = X + 2 + Space * Col, y = Y + 25)
			self.Labels.append(Label)	

		self.Width = 36 * len(self.get_array_x())
		#self.root.geometry(f'{self.Width}x{self.Height}+{self.OffsetX}+{self.OffsetY}')

	def draw_labels(self, X, Y):	# Отрисовка текущих параметров переключения.
		Space = self.Width / (len(LabelsTCU) - 1) + 34

		for Col, Name in  enumerate(LabelsTCU):
			Label = ttk.Label(self.root, text = Name[0], width = 12, anchor = CENTER, relief = "flat", background = BackGroundColor, font = "Verdana 12")
			Label.place(x = X + Space * Col, y = Y)

			Value = ttk.Label(self.root, text = self.get_tcu_data(Name[1]), width = 11, anchor = CENTER, relief = "ridge", background = BackGroundColor, font = "Verdana 12 bold")
			Value.place(x = X + Space * Col, y = Y + 20)
			self.DataTCU[Name[1]] = Value

			ToolTip.ToolTip(Label, Name[2])
			ToolTip.ToolTip(Value, Name[2])

	def update_data(self):	# Обновление текущих параметров переключения.
		for Name in self.DataTCU:
			self.DataTCU[Name].configure(text = self.get_tcu_data(Name))
		self.MainGraph.update_markers()

		if self.Uart.port_status() and self.AutoUpdate.get() != 1:
			self.ReadBtn.config(state='normal')
			self.WriteBtn.config(state='normal')
		else:
			self.ReadBtn.config(state='disabled')
			self.WriteBtn.config(state='disabled')

	def get_tcu_data(self, Parameter):
		return self.Uart.TCU[Parameter]

	def on_closing(self):	# Событие по закрытию окна.
		self.WindowOpen = 0

	def window_close(self):	# Закрытие окна.
		self.root.destroy()

class _Graph:
	def __init__(self, root, x, y, Uart):
		self.x = x
		self.y = y

		self.Uart = Uart

		self.w = 1090
		self.h = 400
		self.Border = 10

		self.N = 0
		self.ArrayX = Tables.TPSGrid

		self.GraphLines = []
		self.GraphPoints = []
		self.PrevGraphLines = []

		self.GraphFocus = 0
		self.CursorPositionL = 0
		self.CursorPositionR = 0

		self.Markers = []

		# Холст.
		self.Box = Canvas(root, width = self.w + 55, height = self.h + 55, bg = BackGroundColor, bd = 0, highlightthickness = 0, relief = 'ridge')

		self.Box.bind('<Enter>', self.focus_event)
		self.Box.bind('<Leave>', self.focus_event)
		self.Box.place(x = self.x, y = self.y)

	def focus_event(self, event):	# Событие смены фокуса окна графика.
		if event.type == '7':
			self.GraphFocus = 1
			self.Box.focus_set()
		elif event.type == '8':
			self.GraphFocus = 0

	def get_cell_value(self, Cells, Position):	# Получение значения из графика.
		Value = 0
		try:
			Value = int(Cells[Position].get())
		except:
			Value = Tables.TablesData[self.N]['Min']
			if Value < 0:
				Value = 0
		return Value

	def move_point(self, Button, State, Cells):	# Перемещение точек.
		if self.GraphFocus:
			Start = self.CursorPositionL
			Stop = self.CursorPositionR

			if Button == 'Up':
				for i in range(Start, Stop + 1):
					Value = self.get_cell_value(Cells, i)
					Value += Tables.TablesData[self.N]['Step']
					Cells[i].delete(0, END)
					Cells[i].insert(0, Value)

			elif Button == 'Down':
				for i in range(Start, Stop + 1):
					Value = self.get_cell_value(Cells, i)
					Value -= Tables.TablesData[self.N]['Step']
					Cells[i].delete(0, END)
					Cells[i].insert(0, Value)

			elif Button == 'Left':
				if self.CursorPositionL > 0:
					self.CursorPositionL -= 1
				if State not in (17, 8209):		# Shift
					self.CursorPositionR = self.CursorPositionL

			elif Button == 'Right':
				if self.CursorPositionR < len(self.ArrayX) - 1:
					self.CursorPositionR += 1
				if State not in (17, 8209):		# Shift
					self.CursorPositionL = self.CursorPositionR

			if Button in ('Up', 'Down'):
				self.update_data(Cells, 0)
				return 2
			elif Button in ('Left', 'Right'):
				self.update_data(Cells, 0)
				return 1
			else:
				return 0

	def print_h_line(self, Value, Min, Max, Leght):	# Отрисовка горизонтальных линий.
		ly = self.h - ((Value - Min)  / (Max - Min)) * (self.h - self.Border * 2) - self.Border
		self.Box.create_line(self.w - 1, ly, self.w + Leght, ly, fill = 'black', width = 2)

		Fill = '#cacfca'
		Width = 2
		if Value == 0:
			Fill = '#000000'
			Width = 3

		self.Box.create_line(2, ly, self.w - 2, ly, fill = Fill, width = Width, dash = 2)

		Str = str(Value)
		self.Box.create_text(self.w + Leght + len(Str) * 5 + 4, ly, font = "Verdana 12", justify = CENTER, fill = 'black', text = Str)

	def print_v_line(self, Value, Min, Max, Leght):	# Отрисовка вертикальных линий.
		lx = self.Border + ((Value - Min)  / (Max - Min)) * (self.w - self.Border * 2)
		self.Box.create_line(lx, self.h - 2, lx, self.h + Leght, fill = 'black', width = 2)
		self.Box.create_line(lx, 2, lx, self.h - 2, fill = '#cacfca', width = 2, dash = 2)

		Str = str(Value)
		self.Box.create_text(lx, self.h + 20, font = "Verdana 12", justify = CENTER, fill = 'black', text = Str)

	def print_line(self, X1, Y1, X2, Y2, LineType):	# Отрисовка линий графика.
		MinX = min(self.ArrayX)
		MaxX = max(self.ArrayX)

		MinY = Tables.TablesData[self.N]['Min']
		MaxY = Tables.TablesData[self.N]['Max']

		lx1 = self.Border + ((X1 - MinX)  / (MaxX - MinX)) * (self.w - self.Border * 2)
		ly1 = self.h - ((Y1 - MinY)  / (MaxY - MinY)) * (self.h - self.Border * 2) - self.Border

		lx2 = self.Border + ((X2 - MinX)  / (MaxX - MinX)) * (self.w - self.Border * 2)
		ly2 = self.h - ((Y2 - MinY)  / (MaxY - MinY)) * (self.h - self.Border * 2) - self.Border

		LineFill  = '#004c99'
		LineWidth = 3
		if LineType == 1:
			LineFill = '#ff6666'
			LineWidth = 2

		Line = self.Box.create_line(lx1, ly1, lx2, ly2, fill = LineFill, width = LineWidth)

		if LineType == 0:
			self.GraphLines.append(Line)
		else:
			self.PrevGraphLines.append(Line)
			return

		R = 3
		Fill = "#cccc00"
		if X1 >= self.ArrayX[self.CursorPositionL] and X1 <= self.ArrayX[self.CursorPositionR]:
			R = 5
			Fill = "#ff1111"
			Tx = lx1
			Ty = ly1 - 20
			if ly1 < 28:
				Ty = ly1 + 20

			if X1 == MinX:
				Tx += 5
			GraphLabel = self.Box.create_text(Tx, Ty, font = "Verdana 10", justify = CENTER, fill = 'black', text = str(Y1))
			self.GraphPoints.append(GraphLabel)
			DownLine = self.Box.create_line(lx1, ly1, lx1, self.h, fill = "#a0a0a0", width = LineWidth)
			self.GraphPoints.append(DownLine)

		Circle = self.Box.create_oval(lx1 - R, ly1 - R, lx1 + R, ly1 + R, fill = Fill, outline = "#004c99")
		self.GraphPoints.append(Circle)

		if X2 == MaxX:
			R2 = 3
			Fill2 = "#cccc00"
			if X2 >= self.ArrayX[self.CursorPositionL] and X2 <= self.ArrayX[self.CursorPositionR]:
				R2 = 5
				Ty = ly2 - 20
				if ly2 < 28:
					Ty = ly2 + 20

				Fill2 = "#ff1111"
				GraphLabel = self.Box.create_text(lx2 - 7, Ty, font = "Verdana 10", justify = CENTER, fill = 'black', text = str(Y2))
				self.GraphPoints.append(GraphLabel)

			Circle = self.Box.create_oval(lx2 - R2, ly2 - R2, lx2 + R, ly2 + R2, fill=Fill2, outline="#004c99")
			self.GraphPoints.append(Circle)

	def redraw(self, N, ArrayX):	# Переотрисовка графика.
		self.N = N
		self.ArrayX = ArrayX
		self.w = len(Tables.TempGrid) * 35
		self.CursorPositionL = 0

		self.Box.delete("all")
		self.Box.create_rectangle(1, 1, self.w - 2, self.h - 2, width = 2, fill = '#fafffd')

		Min = Tables.TablesData[self.N]['Min']
		Max = Tables.TablesData[self.N]['Max']
		
		self.print_h_line(Min, Min, Max, 6)
		self.print_h_line((Max - Min) * 1 // 4 + Min, Min, Max, 6)
		self.print_h_line((Max - Min) * 1 // 2 + Min, Min, Max, 6)
		self.print_h_line((Max - Min) * 3 // 4 + Min, Min, Max, 6)
		self.print_h_line((Max - Min) * 1 // 1 + Min, Min, Max, 6)

		Min = 0
		Max = 0
		for X in ArrayX:
			if X < Min:
				Min = X
			if X > Max:
				Max = X

		for X in ArrayX:
			if X // 10 == X / 10:
				self.print_v_line(X, Min, Max, 6)

	def update_data(self, ArrayY, DrawPrev):	# Обновление графика.
		for Element in self.GraphLines:
			self.Box.delete(Element)
		for Element in self.GraphPoints:
			self.Box.delete(Element)

		if DrawPrev == 1:
			for Element in self.PrevGraphLines:
				self.Box.delete(Element)
			self.PrevGraphLines = []

		self.GraphLines = []
		self.GraphPoints = []

		for i in range(1, len(self.ArrayX), 1):
			x1 = self.ArrayX[i - 1]
			y1 = self.get_cell_value(ArrayY, i - 1)
			x2 = self.ArrayX[i]
			y2 = self.get_cell_value(ArrayY, i)
			if DrawPrev == 1:
				self.print_line(x1, y1, x2, y2, 1)
			self.print_line(x1, y1, x2, y2, 0)

	def update_markers(self):	# Обновление маркеров на графике.
		for Element in self.Markers:
			self.Box.delete(Element)
		self.Markers = []

		ValueX = 0
		if self.ArrayX == Tables.TPSGrid:
			ValueX = self.get_tcu_data('InstTPS')
		elif self.ArrayX == Tables.DeltaRPMGrid:
			ValueX = self.get_tcu_data('DrumRPMDelta')
		elif self.ArrayX == Tables.TempGrid:
			ValueX = self.get_tcu_data('OilTemp')
		else:			
			return

		MinX = min(self.ArrayX)
		MaxX = max(self.ArrayX)
		MinY = Tables.TablesData[self.N]['Min']
		MaxY = Tables.TablesData[self.N]['Max']

		lx = self.Border + ((ValueX - MinX)  / (MaxX - MinX)) * (self.w - self.Border * 2)
		Line = self.Box.create_line(lx, 2, lx, self.h - 2, fill = '#ff9999', width = 2)
		self.Markers.append(Line)
		
		Parameter = Tables.TablesData[self.N]['Parameter']
		if Parameter != '':
			R = 6
			ValueY = self.get_tcu_data(Parameter)
			if ValueY >= MinY and ValueY <= MaxY:
				ly = self.h - ((ValueY - MinY)  / (MaxY - MinY)) * (self.h - self.Border * 2) - self.Border
				Circle = self.Box.create_oval(lx - R, ly - R, lx + R, ly + R, fill='#11ff88', outline="#004c99")
				self.Markers.append(Circle)

	def get_tcu_data(self, Parameter):
		return self.Uart.TCU[Parameter]

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