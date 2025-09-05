from tkinter import *
from tkinter import ttk
from tkinter import font

import tkinter as tk

Parameters = (	  ('uint16_t', 'DrumRPM')
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
				, ('uint8_t', 'DebugMode'))

BackGroundColor = "#d0d0d0"

TPSGrid = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
TempGrid = [-30, -25, -20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120]

LabelsTCU = [['Inst TPS', 'InstTPS'],
			 ['TPS', 'GearChangeTPS'],
			 ['G2 Step', 'LastStep'],
			 ['SLT', 'GearChangeSLT'],
			 ['SLN', 'GearChangeSLN'],
			 ['SLU', 'GearChangeSLU'],
			 ['SLU', 'LastPDRTime'],
			]

			# Номер, название, ось Х, минимум, максимум, описание.
TablesData = [{'N': 0,  'Table': 'SLTGraph', 				'ArrayX': TPSGrid,	'Type': 'uint16_t', 'Min': 100, 	'Max': 800,		'Step': 4, 'Parameter': 'GearChangeSLT', 	'Name': 'Линейное давление SLT от ДПДЗ'}
			, {'N': 1,  'Table': 'SLTTempCorrGraph', 		'ArrayX': TempGrid,	'Type': 'int16_t', 	'Min': -30, 	'Max': 30,		'Step': 1, 'Parameter': '',					'Name': 'Коррекция SLT от температуры в %'}
			, {'N': 2,  'Table': 'SLNGraph', 				'ArrayX': TPSGrid,	'Type': 'uint16_t', 'Min': 100,		'Max': 800,		'Step': 4, 'Parameter': 'GearChangeSLN',	'Name': 'Давление SLN от ДПДЗ (Величина сброса давления)'}
			, {'N': 3,  'Table': 'SLUGear2Graph', 			'ArrayX': TPSGrid,	'Type': 'uint16_t', 'Min': 100, 	'Max': 500,		'Step': 4, 'Parameter': 'GearChangeSLU',	'Name': 'Давление SLU включения второй передачи (SLU B3) от ДПДЗ'}
			, {'N': 4,  'Table': 'SLUGear2TempCorrGraph',	'ArrayX': TempGrid,	'Type': 'int16_t', 	'Min': -30, 	'Max': 30,		'Step': 1, 'Parameter': '',					'Name': 'Коррекция SLU от температуры в %'}
			, {'N': 5,  'Table': 'SLUGear2TPSAdaptGraph', 	'ArrayX': TPSGrid,	'Type': 'int16_t', 	'Min': -32, 	'Max': 32,		'Step': 4, 'Parameter': 'GearChangeSLU',	'Name': 'Адаптация давление SLU включения второй передачи'}			
			, {'N': 6,  'Table': 'SLUGear2TempAdaptGraph',	'ArrayX': TempGrid,	'Type': 'int16_t', 	'Min': -12, 	'Max': 12,		'Step': 1, 'Parameter': '',					'Name': 'Адаптация коррекции SLU от температуры'}
			, {'N': 7,  'Table': 'SLUGear2AddGraph', 		'ArrayX': TPSGrid,	'Type': 'int16_t', 	'Min': -30, 	'Max': 30,		'Step': 2, 'Parameter': '',					'Name': 'Добавка к давлению SLU при повторном включении второй передачи'}
			, {'N': 8,  'Table': 'SLUGear3Graph', 			'ArrayX': TPSGrid,	'Type': 'uint16_t', 'Min': 100, 	'Max': 500,		'Step': 4, 'Parameter': 'GearChangeSLU',	'Name': 'Давление SLU включения третьей передачи (SLU B2) от ДПДЗ'}
			, {'N': 9,  'Table': 'SLUGear3DelayGraph', 		'ArrayX': TPSGrid,	'Type': 'uint16_t', 'Min': 0, 		'Max': 1500,	'Step': 25, 'Parameter': '',				'Name': 'Время удержания SLU от ДПДЗ при включении третьей передачи'}
			, {'N': 10, 'Table': 'SLNGear3Graph', 			'ArrayX': TPSGrid,	'Type': 'uint16_t', 'Min': 100, 	'Max': 800,		'Step': 4, 'Parameter': 'GearChangeSLN',	'Name': 'Давление SLN включения третьей передачи от ДПДЗ'}
			, {'N': 11, 'Table': 'SLNGear3OffsetGraph', 	'ArrayX': TPSGrid,	'Type': 'int16_t', 	'Min': -1000, 	'Max': 1000,	'Step': 25, 'Parameter': '',				'Name': 'Смещение времени включения SLN при включении третьей передачи'}
			]

# Окно редактирования таблиц.
class _TableEditWindow:
	def __init__(self, Uart):
		self.root = tk.Toplevel()
		self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.WindowOpen = 1

		self.Uart = Uart
		self.Cells = []
		self.Labels = []
		self.DataTCU = {}

		self.Width = 1150
		self.Height = 650
		self.OffsetX = 20
		self.OffsetY = 0

		self.CellColor = "#d0ddd0"
		self.ErrorColor = "#e0a0a0"

		self.MainFont = font.Font(size = 10)
		self.root.option_add("*Font", self.MainFont)
		self.root.title('Редакирование таблиц')
		self.root.minsize(self.Width, self.Height)
		self.root.configure(background = BackGroundColor)

		TablesList = []
		for Table in TablesData:
			TablesList.append(Table['Table'])

		self.OnLine = IntVar()
		self.OnLineChk = Checkbutton(self.root, text='Онлайн', variable = self.OnLine, onvalue = 1, offvalue = 0, font = ("Helvetica", 14, 'bold'))
		self.OnLineChk.place(x = 25, y = 14)

		self.ReadBtn = Button(self.root, text = "Считать", width = 8, bg = "#4caa00", command = self.get_table, font = ("Helvetica", 12, 'bold'))
		self.ReadBtn.place(x = 150, y = 8)
		self.WriteBtn = Button(self.root, text = "Записать", width = 8, bg = "#cd5500", command = self.write_table, font = ("Helvetica", 12, 'bold'), state = 'disabled')
		self.WriteBtn.place(x = 300, y = 8)

		self.SaveBtn = Button(self.root, text = "Сохранить в EEPROM", width = 18, bg = "#cdcd00", command = self.write_eeprom, font = ("Helvetica", 12, 'bold'))
		self.SaveBtn.place(x = 450, y = 8)

		self.ExportBtn = Button(self.root, text = "Экспорт", width = 8, bg = "#6495ED", command = self.to_excel, font = ("Helvetica", 12, 'bold'))
		self.ExportBtn.place(x = 700, y = 8)

		self.ImportBtn = Button(self.root, text = "Импорт", width = 8, bg = "#BC8F8F", command = self.from_excel, font = ("Helvetica", 12, 'bold'))
		self.ImportBtn.place(x = 825, y = 8)

		self.ExitBtn = Button(self.root, text = "Закрыть", width = 12, bg = "#f1e71f", command = self.on_closing, font = ("Helvetica", 12, 'bold'))
		self.ExitBtn.place(x = 950, y = 8)

		self.TableBox = ttk.Combobox(self.root, values = TablesList, state = "readonly", width = 22, font = ("Helvetica", 16))
		self.TableBox.place(x = 15, y = 125)
		self.TableBox.current(0)
		self.TableBox.bind("<<ComboboxSelected>>", self.table_selected_event)

		self.TableName = ttk.Label(self.root, text = TablesData[self.TableBox.current()]['Name'], width = 70, anchor = 'w', relief = "flat", background = BackGroundColor, font = "Verdana 12 bold")
		self.TableName.place(x = 320, y = 127)

		# График.
		self.MainGraph = _Graph(self.root, 15, 160, Uart)
		self.draw_table()
		self.MainGraph.redraw(self.TableBox.current(), self.get_array_x())
		if self.Uart.port_status():
			self.get_table()
		self.MainGraph.update_data(self.Cells)

		# Значения TCU Data
		self.draw_labels()

		# Обнаружение нажатия кнопок.
		self.root.bind("<Key>", self.key_pressed)

	def on_closing(self):
		self.WindowOpen = 0

	def window_close(self):
		self.root.destroy()

	def to_excel(self):
		if self.value_check(''):
			Buffer = ''
			for Cell in self.Cells:
				Buffer += Cell.get() + '\t'

			self.root.clipboard_clear()
			self.root.clipboard_append(Buffer[:-1])				

	def from_excel(self):
		Buffer = self.root.clipboard_get().split('\t')
		if len(Buffer) == len(self.get_array_x()):
			for N, Cell in enumerate(self.Cells):
				Cell.delete(0, END)
				Cell.insert(0, str(Buffer[N]))
			self.value_check('')

	def get_array_x(self):
		return TablesData[self.TableBox.current()]['ArrayX']

	def key_pressed(self, event):
		Result = self.MainGraph.move_point(event.keycode, self.Cells)
		if Result:
			self.value_check('')
			if self.OnLine.get() == 1 and Result == 2:
				self.write_table()


	def get_table(self):
		self.Uart.send_command(0xc1, self.TableBox.current(), [])

	def read_table(self):
		print('Поучена таблица', self.Uart.TableNumber)
		if self.Uart.TableNumber == self.TableBox.current():
			if len(self.Uart.TableData) == len(self.get_array_x()):
				
				self.WriteBtn.config(state='normal')
				if self.get_array_x() == TPSGrid:
					for i in range(0, len(TPSGrid), 1):
						self.Cells[i].delete(0, END)
						self.Cells[i].insert(0, self.Uart.TableData[i])
				else:
					for i in range(0, len(TempGrid), 1):
						self.Cells[i].delete(0, END)
						self.Cells[i].insert(0, self.Uart.TableData[i])
				self.MainGraph.update_data(self.Cells)

	def write_table(self):
		Data = []
		for Cell in self.Cells:
			Data.append(int(Cell.get()))
		self.Uart.send_command(0xc8, self.TableBox.current(), Data)
	
	def write_eeprom(self):
		self.Uart.send_command(0xee, self.TableBox.current(), [])

	def value_check(self, event):
		N = self.TableBox.current()
		AllIsOk = 1
		for Cell in self.Cells:
			try:
				Value = int(Cell.get())
				if Value < TablesData[N]['Min']:
					Cell.delete(0, END)
					Cell.insert(0, str(TablesData[N]['Min']))
				elif Value > TablesData[N]['Max']:
					Cell.delete(0, END)
					Cell.insert(0, str(TablesData[N]['Max']))
				else:
					Cell.delete(0, END)
					Cell.insert(0, str(Value))

				Cell.configure(background = self.CellColor)
			except Exception as error:
				Cell.configure(background = self.ErrorColor)
				AllIsOk = 0

		if AllIsOk:
			self.WriteBtn.config(state='normal')
			self.MainGraph.update_data(self.Cells)
			return 1
		else:
			self.WriteBtn.config(state='disabled')
			return 0

	def table_selected_event(self, event):
		self.clear_table()
		self.draw_table()
		self.MainGraph.redraw(self.TableBox.current(), self.get_array_x())
		self.MainGraph.update_data(self.Cells)

		self.TableName.configure(text = TablesData[self.TableBox.current()]['Name'])

		if self.Uart.port_status():
			self.get_table()

	def clear_table(self):
		for Cell in self.Cells:
			Cell.destroy()
		for Label in self.Labels:
			Label.destroy()
		
		self.Cells = []
		self.Labels = []			

	def draw_table(self):
		W = 4
		Y = 600
		Space = 52.5
		if self.get_array_x() == TempGrid:
			Space = 35

		for Col, Value in enumerate(self.get_array_x()):
			Cell = Entry(self.root, justify = "center", bg = self.CellColor, width = W)
			Default = TablesData[self.TableBox.current()]['Min']
			if Default < 0:
				Default = 0

			Cell.insert(0, Default)
			Cell.place(x = 15 + Space * Col, y = Y)
			Cell.bind("<FocusOut>", self.value_check)
			self.Cells.append(Cell)	

			Label = ttk.Label(self.root, text = Value, width = W, anchor = CENTER, relief = "flat", background = BackGroundColor)
			Label.place(x = 17 + Space * Col, y = Y + 25)
			self.Labels.append(Label)	

		self.Width = 36 * len(self.get_array_x())
		#self.root.geometry(f'{self.Width}x{self.Height}+{self.OffsetX}+{self.OffsetY}')

	def draw_labels(self):
		Y = 57
		Space = self.Width / (len(LabelsTCU) - 3)

		for Col, Name in  enumerate(LabelsTCU):
			Label = ttk.Label(self.root, text = Name[0], width = 12, anchor = CENTER, relief = "flat", background = BackGroundColor, font = "Verdana 12")
			Label.place(x = 17 + Space * Col, y = Y)
			
			Value = ttk.Label(self.root, text = self.get_tcu_data(Name[1]), width = 11, anchor = CENTER, relief = "ridge", background = BackGroundColor, font = "Verdana 12 bold")
			Value.place(x = 17 + Space * Col, y = Y + 20)
			self.DataTCU[Name[1]] = Value

	def update_labels(self):
		for Name in self.DataTCU:
			self.DataTCU[Name].configure(text = self.get_tcu_data(Name))
		self.MainGraph.update_markers()

		if self.Uart.port_status():
			self.ReadBtn.config(state='normal')
			self.WriteBtn.config(state='normal')
			self.SaveBtn.config(state='normal')
		else:
			self.ReadBtn.config(state='disabled')
			self.WriteBtn.config(state='disabled')
			self.SaveBtn.config(state='disabled')

	def get_tcu_data(self, Parameter):
		return self.Uart.TCU[Parameter]

class _Graph:
	def __init__(self, root, x, y, Uart):
		self.x = x
		self.y = y

		self.Uart = Uart

		self.w = 1090
		self.h = 400
		self.Border = 10

		self.N = 0
		self.ArrayX = TPSGrid

		self.GraphLines = []
		self.GraphPoints = []
		self.GraphLabel = 0

		self.GraphFocus = 0
		self.CursorPosition = 0

		self.Markers = []

		# Холст.
		self.Box = Canvas(root, width = self.w + 55, height = self.h + 55, bg = BackGroundColor, bd = 0, highlightthickness = 0, relief = 'ridge')

		self.Box.bind('<Enter>', self.focus_event)
		self.Box.bind('<Leave>', self.focus_event)
		self.Box.place(x = self.x, y = self.y)

	def focus_event(self, event):
		if event.type == '7':
			self.GraphFocus = 1
			self.Box.focus_set()
		elif event.type == '8':
			self.GraphFocus = 0

	def get_cell_value(self, Cells, Position):
		Value = 0
		try:
			Value = int(Cells[Position].get())
		except:
			Value = TablesData[self.N]['Min']
			if Value < 0:
				Value = 0
		return Value

	def move_point(self, Button, Cells):
		if self.GraphFocus:
			if Button == 111:	# Up
				Value = self.get_cell_value(Cells, self.CursorPosition)
				Value += TablesData[self.N]['Step']
				Cells[self.CursorPosition].delete(0, END)
				Cells[self.CursorPosition].insert(0, Value)

			elif Button == 116:	# Down
				Value = self.get_cell_value(Cells, self.CursorPosition)
				Value -= TablesData[self.N]['Step']
				Cells[self.CursorPosition].delete(0, END)
				Cells[self.CursorPosition].insert(0, Value)

			elif Button == 113:	# Left
				if self.CursorPosition > 0:
					self.CursorPosition -= 1
			elif Button == 114:	# Right
				if self.CursorPosition < len(self.ArrayX) - 1:
					self.CursorPosition += 1

			if Button in (111, 116):
				self.update_data(Cells)
				return 2
			elif Button in (113, 114):
				self.update_data(Cells)
				return 1
			else:
				return 0

	def print_h_line(self, Value, Min, Max, Leght):
		ly = self.h - ((Value - Min)  / (Max - Min)) * (self.h - self.Border * 2) - self.Border
		self.Box.create_line(self.w - 1, ly, self.w + Leght, ly, fill = 'black', width = 2)
		self.Box.create_line(2, ly, self.w - 2, ly, fill = '#cacfca', width = 2, dash = 2)

		Str = str(Value)
		self.Box.create_text(self.w + Leght + len(Str) * 5 + 4, ly, font = "Verdana 12", justify = CENTER, fill = 'black', text = Str)

	def print_v_line(self, Value, Min, Max, Leght):
		lx = self.Border + ((Value - Min)  / (Max - Min)) * (self.w - self.Border * 2)
		self.Box.create_line(lx, self.h - 2, lx, self.h + Leght, fill = 'black', width = 2)
		self.Box.create_line(lx, 2, lx, self.h - 2, fill = '#cacfca', width = 2, dash = 2)

		Str = str(Value)
		self.Box.create_text(lx, self.h + 20, font = "Verdana 12", justify = CENTER, fill = 'black', text = Str)

	def print_line(self, X1, Y1, X2, Y2):
		MinX = min(self.ArrayX)
		MaxX = max(self.ArrayX)

		MinY = TablesData[self.N]['Min']
		MaxY = TablesData[self.N]['Max']

		lx1 = self.Border + ((X1 - MinX)  / (MaxX - MinX)) * (self.w - self.Border * 2)
		ly1 = self.h - ((Y1 - MinY)  / (MaxY - MinY)) * (self.h - self.Border * 2) - self.Border

		lx2 = self.Border + ((X2 - MinX)  / (MaxX - MinX)) * (self.w - self.Border * 2)
		ly2 = self.h - ((Y2 - MinY)  / (MaxY - MinY)) * (self.h - self.Border * 2) - self.Border

		Line = self.Box.create_line(lx1, ly1, lx2, ly2, fill = '#004c99', width = 3)
		self.GraphLines.append(Line)

		R = 3
		Fill = "#cccc00"
		if self.ArrayX[self.CursorPosition] == X1:
			R = 5
			Fill = "#ff1111"
			Tx = lx1
			Ty = ly1 - 20
			if ly1 < 28:
				Ty = ly1 + 20

			if X1 == MinX:
				Tx += 5
			self.GraphLabel = self.Box.create_text(Tx, Ty, font = "Verdana 10", justify = CENTER, fill = 'black', text = str(Y1))

		Circle = self.Box.create_oval(lx1 - R, ly1 - R, lx1 + R, ly1 + R, fill=Fill, outline="#004c99")
		self.GraphPoints.append(Circle)

		if X2 == MaxX:
			R2 = 3
			Fill2 = "#cccc00"
			if self.ArrayX[self.CursorPosition] == X2:
				R2 = 5
				Ty = ly2 - 20
				if ly2 < 28:
					Ty = ly2 + 20

				Fill2 = "#ff1111"
				self.GraphLabel = self.Box.create_text(lx2 - 7, Ty, font = "Verdana 10", justify = CENTER, fill = 'black', text = str(Y2))

			Circle = self.Box.create_oval(lx2 - R2, ly2 - R2, lx2 + R, ly2 + R2, fill=Fill2, outline="#004c99")
			self.GraphPoints.append(Circle)

	def redraw(self, N, ArrayX):
		self.N = N
		self.ArrayX = ArrayX
		self.w = len(TempGrid) * 35
		self.CursorPosition = 0

		self.Box.delete("all")
		self.Box.create_rectangle(1, 1, self.w - 2, self.h - 2, width = 2, fill = '#fafffd')

		Min = TablesData[self.N]['Min']
		Max = TablesData[self.N]['Max']
		
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

	def update_data(self, ArrayY):
		for Element in self.GraphLines:
			self.Box.delete(Element)
		for Element in self.GraphPoints:
			self.Box.delete(Element)
		self.Box.delete(self.GraphLabel)

		self.GraphLines = []
		self.GraphPoints = []

		for i in range(1, len(self.ArrayX), 1):
			x1 = self.ArrayX[i - 1]
			y1 = self.get_cell_value(ArrayY, i - 1)
			x2 = self.ArrayX[i]
			y2 = self.get_cell_value(ArrayY, i)
			self.print_line(x1, y1, x2, y2)

	def update_markers(self):
		for Element in self.Markers:
			self.Box.delete(Element)
		self.Markers = []

		ValueX = 0
		if self.ArrayX == TPSGrid:
			ValueX = self.get_tcu_data('InstTPS')
		elif self.ArrayX == TempGrid:
			ValueX = self.get_tcu_data('OilTemp')
		else:
			return

		MinX = min(self.ArrayX)
		MaxX = max(self.ArrayX)
		MinY = TablesData[self.N]['Min']
		MaxY = TablesData[self.N]['Max']

		lx = self.Border + ((ValueX - MinX)  / (MaxX - MinX)) * (self.w - self.Border * 2)
		Line = self.Box.create_line(lx, 2, lx, self.h - 2, fill = '#ff9999', width = 2)
		self.Markers.append(Line)
		
		Parameter = TablesData[self.N]['Parameter']
		if Parameter != '':
			R = 6
			ValueY = self.get_tcu_data(Parameter)
			if ValueY >= MinY and ValueY <= MaxY:
				ly = self.h - ((ValueY - MinY)  / (MaxY - MinY)) * (self.h - self.Border * 2) - self.Border
				Circle = self.Box.create_oval(lx - R, ly - R, lx + R, ly + R, fill='#11ff88', outline="#004c99")
				self.Markers.append(Circle)

	def get_tcu_data(self, Parameter):
		return self.Uart.TCU[Parameter]
