from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
import tkinter as tk
import time

import ToolTip
import Tables

BackGroundColor = "#d0d0d0"

GraphParemeters = [{'Name': '2>1', 'Color': '#C3D69B'}
					, {'Name': '1>2', 'Color': '#77933C'}
					, {'Name': '3>2', 'Color': '#93CDDD'}
					, {'Name': '2>3', 'Color': '#31859C'}
					, {'Name': '4>3', 'Color': '#FFC000'}
					, {'Name': '3>4', 'Color': '#E46C0A'}
					, {'Name': '5>4', 'Color': '#B3A2C7'}
					, {'Name': '4>5', 'Color': '#604A7B'}
					]

TableN = 0
for Table in Tables.TablesData:
	if Table['Table'] == 'GearSpeedGraphs':
		TableN = Table['N']

ArrayX = Tables.TPSGrid

# Окно редактирования таблиц.
class _SpeedEditWindow:
	def __init__(self, Uart):
		self.root = tk.Toplevel()
		self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.WindowOpen = 1
		self.WindowName = 'EditSpeed'

		self.SpeedData = []

		for k in range(0, 8, 1):
			TempArray = []
			for i in range(0, len(ArrayX), 1):
				TempArray.append(0)
			self.SpeedData.append(TempArray)

		self.Uart = Uart
		self.Labels = []
		self.DataTCU = {}

		self.GetNewTable = 0

		self.Width = 1180
		self.Height = 700
		self.OffsetX = 20
		self.OffsetY = 0

		self.CellColor = "#d0ddd0"
		self.ErrorColor = "#e0a0a0"

		self.MainFont = font.Font(size = 10)
		self.root.option_add("*Font", self.MainFont)
		self.root.title('Редакирование скоростей переключения передач')
		self.root.minsize(self.Width, self.Height)
		self.root.configure(background = BackGroundColor)

		# Индикатор ответа ЭБУ.
		self.Answer = _LightIndicator(self.root, 'A', 60, 10)

		# Галка "Онлайн".
		self.OnLine = IntVar()
		self.OnLineChk = Checkbutton(self.root, text='Онлайн', variable = self.OnLine, onvalue = 1, offvalue = 0, background = BackGroundColor, font = ("Helvetica", 14, 'bold'))
		self.OnLineChk.place(x = 120, y = 10)

		# Чтение/Запись
		self.ReadBtn = Button(self.root, text = "Считать", width = 8, bg = "#4caa00", command = self.get_table, font = ("Helvetica", 12, 'bold'))
		self.ReadBtn.place(x = 15, y = 45)
		self.WriteBtn = Button(self.root, text = "Записать", width = 8, bg = "#cd5500", command = self.write_table, font = ("Helvetica", 12, 'bold'), state = 'disabled')
		self.WriteBtn.place(x = 125, y = 45)

		self.EReadBtn = Button(self.root, text = "Считать из EEPROM", width = 19, bg = "#adff2f", command = self.read_eeprom, font = ("Helvetica", 12, 'bold'))
		self.EReadBtn.place(x = 18, y = 140)
		self.ESaveBtn = Button(self.root, text = "Сохранить в EEPROM", width = 19, bg = "#ff8c00", command = self.write_eeprom, font = ("Helvetica", 12, 'bold'))
		self.ESaveBtn.place(x = 18, y = 185)

		# Экспорт / Импорт.
		self.ExportBtn = Button(self.root, text = "Экспорт", width = 8, bg = "#6495ed", command = self.to_excel, font = ("Helvetica", 12, 'bold'))
		self.ExportBtn.place(x = 15, y = 270)
		self.ImportBtn = Button(self.root, text = "Импорт", width = 8, bg = "#bc8f8f", command = self.from_excel, font = ("Helvetica", 12, 'bold'))
		self.ImportBtn.place(x = 125, y = 270)

		# Сброс таблиц.
		self.TableResetBtn = Button(self.root, text = "Сброс\nтаблиц", width = 8, bg = "#B44444", command = self.reset_tables, font = ("Helvetica", 12, 'bold'))
		self.TableResetBtn.place(x = 75, y = 400)

		# График.
		self.MainGraph = _Graph(self.root, 280, 10, Uart)
		self.MainGraph.redraw()
		if self.Uart.port_status():
			self.get_table()
		self.MainGraph.update_data(self.SpeedData)

		# Выход.
		self.ExitBtn = Button(self.root, text = "Закрыть", width = 12, height = 3, bg = "#cd853f", command = self.on_closing, font = ("Helvetica", 12, 'bold'))
		self.ExitBtn.place(x = 55, y = 550)

		# Подсказка по клавишам.
		Label = ttk.Label(self.root, text = 'Ctrl + вверх/вниз - смена текущего графика', relief = 'flat', font = ("Helvetica", 12), background = BackGroundColor, wraplength = 250)
		Label.place(x = 50, y = 630)

		self.draw_graph_buttons()

		self.add_tooltip()

		# Обнаружение нажатия кнопок.
		self.root.bind("<Key>", self.key_pressed)

	def add_tooltip(self):	# Вставка подсказок.
		ToolTip.ToolTip(self.ReadBtn, "Считать таблицу из оперативной памяти ЭБУ")
		ToolTip.ToolTip(self.WriteBtn, "Отправить таблицу в ЭБУ. Таблица будет записана в ОЗУ, для сохранения изменений необходимо перенести таблицу в EEPROM.")
		
		ToolTip.ToolTip(self.Answer.Box, "Индикатор ответа ЭБУ на команду. Красный - команда не принята. Зелёный - команда успешно обработана.")

		ToolTip.ToolTip(self.EReadBtn, "Считать все таблицы из EEPROM в ОЗУ")
		ToolTip.ToolTip(self.ESaveBtn, "Сохранить все таблицы из ОЗУ в EEPROM")

		ToolTip.ToolTip(self.ExportBtn, "Экспорт текущей таблицы в буфер обмена. Значения передаюся в буфер с разделителем-табуляцией для дальнейшей вставки в Excel.")
		ToolTip.ToolTip(self.ImportBtn, "Импорт таблицы из буфер обмена. Значения должны быть с разделителем-табуляцией и в таком же количестве.")

		ToolTip.ToolTip(self.TableResetBtn, "Сброс всех таблиц текущего окна. Значения заменяются на начальные из прошивки и производтся запись в EEPROM. Можно использовать в том числе для первоначальной записи таблиц в EEPROM.")

		ToolTip.ToolTip(self.ExitBtn, "Закрыть окно.")

		ToolTip.ToolTip(self.BtnZero, "Обнуление графика")

	def draw_graph_buttons(self):	# Отрисовка кнопок на графике.
		X = self.MainGraph.x - 30
		Y = self.MainGraph.y + self.MainGraph.h / 2
		H = 13

		self.BtnBuildLine = Button(self.root, text = "L", width = 1, bg = "#bcbcbc", command = self.build_line, font = ("Helvetica", 10, 'bold'), border="2px", state = 'normal')
		self.BtnBuildLine.place(x = X, y = Y - H - 95, width = 25, height = 25)

		self.BtnZero = Button(self.root, text = "0", width = 1, bg = "#bcbcbc", command = lambda: self.move_graph(0), font = ("Helvetica", 10, 'bold'), border="2px")
		self.BtnZero.place(x = X, y = Y - H, width = 25, height = 25)

		Button(self.root, text = "+", width = 1, bg = "#bcbcbc", command = lambda: self.move_graph(1), font = ("Helvetica", 10, 'bold'), border="2px").place(x = X, y = Y - H - 40, width = 25, height = 25)
		Button(self.root, text = "-", width = 1, bg = "#bcbcbc", command = lambda: self.move_graph(-1), font = ("Helvetica", 10, 'bold'), border="2px").place(x = X, y = Y - H + 40, width = 25, height = 25)

	def read_table(self):	# Событие при получении данных из ЭБУ.
		if self.Uart.TableNumber == TableN:
			if len(self.Uart.TableData) == len(ArrayX) * 8:
				self.SpeedData = []

				for k in range(0, 8, 1):	# 0-20
					TempArray = []
					for j in range(0, len(ArrayX), 1):	# 0-7
						TempArray.append(self.Uart.TableData[j * 8 + k])
					self.SpeedData.append(TempArray)

				self.WriteBtn.config(state='normal')
				self.MainGraph.update_data(self.SpeedData)
				self.GetNewTable = 0
				self.Answer.update(0)

	def get_table(self):	# Команда на получение таблицы из ЭБУ.
		self.Answer.update(1)
		self.GetNewTable = 1
		self.Uart.send_command('GET_TABLE_COMMAND', TableN, [], self.root)

	def key_pressed(self, event):	# Событие по нажатию кнопки на клавиатуре.
		State = event.state
		for Mod in Tables.BadMods:
			if State >= Mod:
				State -= Mod

		Result = self.MainGraph.move_point(event.keysym, State, self.SpeedData)
		if Result:
			self.value_check('')
			if self.OnLine.get() == 1 and Result == 2:
				self.write_table()

	def build_line(self):
		Start = self.MainGraph.CursorPositionL
		Stop = self.MainGraph.CursorPositionR
		if Start == Stop:
			Start = 0
			Stop = len(self.SpeedData[self.MainGraph.CurrentGraph]) - 1

		ArrayLen = Stop - Start
		Min = self.SpeedData[self.MainGraph.CurrentGraph][Start]
		Max = self.SpeedData[self.MainGraph.CurrentGraph][Stop]
		Step = (Max - Min) / ArrayLen

		print(ArrayLen, Min, Max, Step)

		for i in range(0, ArrayLen + 1):
			Value = round(Min + Step * i)
			self.SpeedData[self.MainGraph.CurrentGraph][Start + i] = Value
		self.value_check('')

	def move_graph(self, Where):	# Перемещение точек на графике.
		Step = Tables.TablesData[TableN]['Step']
		Start = 0
		Stop = len(self.SpeedData[self.MainGraph.CurrentGraph]) - 1

		for i in range(Start, Stop + 1):
			if Where == 0:
				self.SpeedData[self.MainGraph.CurrentGraph][i] = 0
			elif Where == 1:
				self.SpeedData[self.MainGraph.CurrentGraph][i] += Step
			elif Where == -1:
				self.SpeedData[self.MainGraph.CurrentGraph][i] -= Step

		self.value_check('')
		if self.OnLine.get() == 1:
			self.write_table()		

	def to_excel(self):	# Экспорт данных в Excel.
		if self.value_check(''):
			Buffer = ''
			for n, Row in enumerate(self.SpeedData):
				Buffer += GraphParemeters[n]['Name'] + '\t'
				
				for Col in Row:
					Buffer += str(Col) + '\t'
				Buffer = Buffer[:-1]
				Buffer += '\n'

			self.root.clipboard_clear()
			self.root.clipboard_append(Buffer[:-1])				

	def from_excel(self):	# Импорт данных из Excel.
		Buffer = self.root.clipboard_get().split('\n')[:-1]
		if len(Buffer) == 8:
			Ok = 1
			# Проверяем длину каждой строки.
			for k, BR in enumerate(Buffer):
				Row = BR.split('\t')
				if len(Row) != len(ArrayX) + 1 or Row[0] != GraphParemeters[k]['Name']:
					Ok = 0
					break
			if Ok == 1:
				for k, BR in enumerate(Buffer):
					Row = BR.split('\t')
					for j, Cell in enumerate(Row):
						if j > 0:
							self.SpeedData[k][j - 1] = Cell
				self.value_check('')

	def write_table(self):	# Команда на запись таблицы в ОЗУ ЭБУ.
		self.Answer.update(1)
		Data = []
		Rows = len(self.SpeedData)		# 8
		Cols = len(self.SpeedData[0])	# 21
		for j in range(Cols):
			for k in range(Rows):
				Data.append(self.SpeedData[k][j])

		self.Uart.send_command('NEW_TABLE_DATA', TableN, Data, self.root)

	def read_eeprom(self):	# Команда на чтение EEPROM.
		self.Answer.update(1)
		self.Uart.send_command('READ_EEPROM_SPEED_COMMAND', TableN, [], self.root)

	def write_eeprom(self):	# Команда на запись EEPROM.
		self.Answer.update(1)
		self.Uart.send_command('WRITE_EEPROM_SPEED_COMMAND', TableN, [], self.root)
	
	def reset_tables(self):	# Команда сброса таблиц в ЭБУ.
		if messagebox.askyesno('Сброс таблиц', 'Перезаписать EEPROM ВСЕX таблицы текущего окна значениями из прошивки?', parent = self.root):
			time.sleep(0.5)
			self.Answer.update(1)
			self.Uart.send_command('TABLES_INIT_SPEED_COMMAND', TableN, [], self.root)

	def value_check(self, event):	# Проверка и исправление значений таблицы.
		for k in range(0, 8, 1):
			for i in range(0, len(ArrayX), 1):
				try:
					self.SpeedData[k][i] = int(self.SpeedData[k][i])
				except:
					self.SpeedData[k][i] = 0

				if self.SpeedData[k][i] < Tables.TablesData[TableN]['Min']:
					self.SpeedData[k][i] = Tables.TablesData[TableN]['Min']
				elif self.SpeedData[k][i] > Tables.TablesData[TableN]['Max']:
					self.SpeedData[k][i] = Tables.TablesData[TableN]['Max']
		self.MainGraph.update_data(self.SpeedData)
		return 1

	def update_data(self):	# Обновление текущих параметров переключения.
		for Name in self.DataTCU:
			self.DataTCU[Name].configure(text = self.get_tcu_data(Name))
		self.MainGraph.update_markers()

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

		self.w = 850
		self.h = 650
		self.Border = 10

		self.GraphLines = []
		self.GraphPoints = []

		self.GraphFocus = 0
		self.CursorPositionL = 0
		self.CursorPositionR = 0
		self.CurrentGraph = 0

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

	def move_point(self, Button, State, SpeedData):	# Перемещение точек.
		if self.GraphFocus:
			Start = self.CursorPositionL
			Stop = self.CursorPositionR

			if Button == 'Up':
				if State == 4:		# Ctrl
					self.CurrentGraph = min(self.CurrentGraph + 1, len(GraphParemeters) - 1)
				else:
					for i in range(Start, Stop + 1):
						SpeedData[self.CurrentGraph][i] += Tables.TablesData[TableN]['Step']
			elif Button == 'Down':
				if State == 4:		# Ctrl
					self.CurrentGraph = max(self.CurrentGraph - 1, 0)
				else:
					for i in range(Start, Stop + 1):
						SpeedData[self.CurrentGraph][i] -= Tables.TablesData[TableN]['Step']

			elif Button == 'Left':
				if self.CursorPositionL > 0:
					self.CursorPositionL -= 1
				if State != 1:		# Shift
					self.CursorPositionR = self.CursorPositionL
					
			elif Button == 'Right':
				if self.CursorPositionR < len(ArrayX) - 1:
					self.CursorPositionR += 1
				if State != 1:		# Shift
					self.CursorPositionL = self.CursorPositionR
			if Button in ('Up', 'Down'):
				self.update_data(SpeedData)
				return 2
			elif Button in ('Left', 'Right'):
				self.update_data(SpeedData)
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

	def print_line(self, X1, Y1, X2, Y2, Color, N):	# Отрисовка линий графика.
		MinX = min(ArrayX)
		MaxX = max(ArrayX)

		MinY = Tables.TablesData[TableN]['Min']
		MaxY = Tables.TablesData[TableN]['Max']

		lx1 = self.Border + ((X1 - MinX)  / (MaxX - MinX)) * (self.w - self.Border * 2)
		ly1 = self.h - ((Y1 - MinY)  / (MaxY - MinY)) * (self.h - self.Border * 2) - self.Border

		lx2 = self.Border + ((X2 - MinX)  / (MaxX - MinX)) * (self.w - self.Border * 2)
		ly2 = self.h - ((Y2 - MinY)  / (MaxY - MinY)) * (self.h - self.Border * 2) - self.Border

		LineFill  = Color
		LineWidth = 1.5
		if N == self.CurrentGraph:
			LineWidth = 3.5

		Line = self.Box.create_line(lx1, ly1, lx2, ly2, fill = LineFill, width = LineWidth)
		self.GraphLines.append(Line)

		if X2 == MaxX:
			Circle = self.Box.create_oval(lx2 - 15 - 20, ly2 + 13 - 10, lx2 -15 + 20, ly2 + 13 + 10, fill="white", outline="white")
			self.GraphLines.append(Circle)
			Font = "Verdana 10"
			if N == self.CurrentGraph:
				Font = "Verdana 10 bold"
			GraphName = self.Box.create_text(lx2 - 15, ly2 + 13, font = Font, justify = CENTER, fill = Color, text = GraphParemeters[N]['Name'])
			self.GraphLines.append(GraphName)

		if N == self.CurrentGraph:
			R = 3
			Fill = "#cccc00"
			if X1 >= ArrayX[self.CursorPositionL] and X1 <= ArrayX[self.CursorPositionR]:
				R = 5
				Fill = "#ff1111"
				Tx = lx1
				Ty = ly1 - 20
				if ly1 < 28:
					Ty = ly1 + 20

				if X1 == MinX:
					Tx += 5

				TR = 12
				Circle = self.Box.create_oval(Tx - TR, Ty - TR, Tx + TR, Ty + TR, fill="white", outline="white")
				GraphLabel = self.Box.create_text(Tx, Ty, font = "Verdana 10", justify = CENTER, fill = 'black', text = str(Y1))
				self.GraphPoints.append(Circle)
				self.GraphPoints.append(GraphLabel)

				DownLine = self.Box.create_line(lx1, ly1, lx1, self.h, fill = "#a0a0a0", width = LineWidth)
				self.GraphPoints.append(DownLine)

			Circle = self.Box.create_oval(lx1 - R, ly1 - R, lx1 + R, ly1 + R, fill = Fill, outline = "#004c99")
			self.GraphPoints.append(Circle)

			if X2 == MaxX:
				R2 = 3
				Fill2 = "#cccc00"
				if X2 >= ArrayX[self.CursorPositionL] and X2 <= ArrayX[self.CursorPositionR]:
					R2 = 5
					Ty = ly2 - 20
					if ly2 < 28:
						Ty = ly2 + 20

					TR = 12
					Fill2 = "#ff1111"
					Circle = self.Box.create_oval(lx2 - 7 - TR, Ty - TR, lx2 - 7 + TR, Ty + TR, fill="white", outline="white")
					GraphLabel = self.Box.create_text(lx2 - 7, Ty, font = "Verdana 10", justify = CENTER, fill = 'black', text = str(Y1))
					self.GraphPoints.append(Circle)
					self.GraphPoints.append(GraphLabel)

					DownLine = self.Box.create_line(lx2, ly2, lx2, self.h, fill = "#a0a0a0", width = LineWidth)
					self.GraphPoints.append(DownLine)

				Circle = self.Box.create_oval(lx2 - R2, ly2 - R2, lx2 + R, ly2 + R2, fill=Fill2, outline="#004c99")
				self.GraphPoints.append(Circle)

	def redraw(self):	# Переотрисовка графика.
		self.CursorPositionL = 0

		self.Box.delete("all")
		self.Box.create_rectangle(1, 1, self.w - 2, self.h - 2, width = 2, fill = '#fafffd')

		Min = Tables.TablesData[TableN]['Min']
		Max = Tables.TablesData[TableN]['Max']

		for i in range(Max // 10 + 1):
			self.print_h_line(i * 10, Min, Max, 6)

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

	def update_data(self, SpeedData):	# Обновление графика.
		for Element in self.GraphLines:
			self.Box.delete(Element)
		for Element in self.GraphPoints:
			self.Box.delete(Element)

		self.GraphLines = []
		self.GraphPoints = []

		for n, ArrayY in enumerate(SpeedData):
			if ArrayY != SpeedData[self.CurrentGraph]:
				for i in range(1, len(ArrayX), 1):
					x1 = ArrayX[i - 1]
					y1 = ArrayY[i - 1]
					x2 = ArrayX[i]
					y2 = ArrayY[i]
					self.print_line(x1, y1, x2, y2, GraphParemeters[n]['Color'], n)

		ArrayY = SpeedData[self.CurrentGraph]
		for i in range(1, len(ArrayX), 1):
			x1 = ArrayX[i - 1]
			y1 = ArrayY[i - 1]
			x2 = ArrayX[i]
			y2 = ArrayY[i]
			self.print_line(x1, y1, x2, y2, GraphParemeters[self.CurrentGraph]['Color'], self.CurrentGraph)

	def update_markers(self):	# Обновление маркеров на графике.
		for Element in self.Markers:
			self.Box.delete(Element)
		self.Markers = []

		ValueX = self.get_tcu_data('InstTPS')
		ValueY = self.get_tcu_data('CarSpeed')

		MinX = min(ArrayX)
		MaxX = max(ArrayX)
		MinY = Tables.TablesData[TableN]['Min']
		MaxY = Tables.TablesData[TableN]['Max']

		lx = self.Border + ((ValueX - MinX)  / (MaxX - MinX)) * (self.w - self.Border * 2)
		Line = self.Box.create_line(lx, 2, lx, self.h - 2, fill = '#ff0000', width = 2)
		self.Markers.append(Line)

		ly = self.h - ((ValueY - MinY)  / (MaxY - MinY)) * (self.h - self.Border * 2) - self.Border
		Line = self.Box.create_line(2, ly, self.w - 2, ly, fill = '#0000ff', width = 2, dash = 3)
		self.Markers.append(Line)


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