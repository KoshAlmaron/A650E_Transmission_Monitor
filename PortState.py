from tkinter import *
from tkinter import font
from tkinter import ttk

from tkinter import filedialog
from tkinter import messagebox

import tkinter as tk

from datetime import datetime
import time
import json
import os

import ToolTip
import Tables

BackGroundColor = "#d0d0d0"

SelectorPins = ('P', 'R', 'N', 'D', '3', '2', 'D4', 'L')

# Окно редактирования настроек.
class _PortStateEditWindow:
	def __init__(self, Uart):
		self.root = tk.Toplevel()
		self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.WindowOpen = 1
		self.WindowName = 'PortState'

		self.PortStateDict = {}

		self.Uart = Uart

		self.Width = 860
		self.Height = 710
		self.OffsetX = 20
		self.OffsetY = 0

		self.MainFont = font.Font(size = 10)
		self.root.option_add("*Font", self.MainFont)
		self.root.title('Состояние выводов МК')
		self.root.minsize(self.Width, self.Height)
		self.root.configure(background = BackGroundColor)

		# Добавление строк состояния портов.
		self.draw_port_state()
		# Добавление индикаторов селектора.
		self.draw_selector_state()

		# Индикатор ответа ЭБУ.
		self.Answer = _LightIndicator(self.root, 'A', 670, 22)

		# Выход.
		self.ExitBtn = Button(self.root, text = "Закрыть", width = 12, height = 2, bg = "#cd853f", command = self.on_closing, font = ("Helvetica", 12, 'bold'))
		self.ExitBtn.place(x = self.Width - 145, y = 10)

	def draw_port_state(self):
		MaxRows = 24
		StartY = 20
		DeltaY = 24

		StartX = 30
		DeltaX = 220

		Row = 0
		X = StartX
		Y = StartY
		for Key in Tables.ArduinoPins:
			if Row >= MaxRows:
				X += DeltaX
				Row = 0

			Y = StartY + DeltaY * Row
			LabelText = Key + '   I   ' + Tables.ArduinoPins[Key]['Port']
			if Tables.ArduinoPins[Key]['Functions'] != '':
			 	LabelText += ' (' + Tables.ArduinoPins[Key]['Functions'] + ')'
			Label = ttk.Label(self.root, text = LabelText, relief = 'raised', font = self.MainFont, background = 'gray', padding = 2, width = 23)
			Label.place(x = X, y = Y)

			self.PortStateDict[Key] = Label

			Row += 1

		self.Height = StartY + DeltaY * MaxRows + 30
		self.root.minsize(self.Width, self.Height)

	def draw_selector_state(self):
		self.SelectorLabels = []
		X = 750
		StartY = 125
		DeltaY = 50

		for n, Pin in enumerate(SelectorPins):
			Y = StartY + DeltaY * n
			Label = _SelectorIndicator(self.root, Pin, X, Y)
			Label.w = 80
			Label.h = 80
			self.SelectorLabels.append(Label)

	def update_port_state(self):
		self.Answer.update(0)
		for Key in Tables.ArduinoPins:
			PortData = self.get_port_state(Tables.ArduinoPins[Key]['Port'])

			if PortData['State'] == 0:
				self.PortStateDict[Key].config(background = '#c0c0c0')
			else:
				self.PortStateDict[Key].config(background = '#00bb00')

			LabelText = self.PortStateDict[Key]['text']
			if PortData['Type'] == 0:
				LabelText = LabelText.replace(' O ', ' I ')
				self.PortStateDict[Key].config(text = LabelText)
				self.PortStateDict[Key].config(foreground = 'black')
			else:
				LabelText = LabelText.replace(' I ', ' O ')
				self.PortStateDict[Key].config(text = LabelText)
				self.PortStateDict[Key].config(foreground = '#990000')

		SelectorByte = self.Uart.PortData[self.get_byte_number('L') + 2]
		for i in range(0, 8):
			self.SelectorLabels[i].update(self.get_bit(SelectorByte, i))

	def get_port_state(self, Port):
		PortLeter = Port[1:2]
		PortNumber = int(Port[2:3])

		PortState = {}
		PortByte = self.Uart.PortData[self.get_byte_number(PortLeter)]
		PortState['State'] = self.get_bit(PortByte, PortNumber)
		PortByte = self.Uart.PortData[self.get_byte_number(PortLeter) + 1]
		PortState['Type'] = self.get_bit(PortByte, PortNumber)

		#print(Port, bin(PortByte), PortState)
		return PortState

	def get_bit(self, Number, N):
		Binary = bin(Number)[2:]
		Binary = ('00000000' + Binary)[-8:]	# Добавляем недостающие нули слева.

		Bit = Binary[7 - N: 8 - N]
		if Bit == '':
			Bit = 0
		return int(Bit)

	def get_byte_number(self, Letter):
		N = ord(Letter) - 65
		if N > 8:	# В Atmege нет порта I.
			N -= 1
		if N < 0 or N > 11:
			return -1
		return N * 2

	def get_port_packet(self):
		if self.Uart.PortReading == 1:
			self.Answer.update(1)
			self.Uart.send_command('GET_PORTS_STATE', 0, [])

	def on_closing(self):	# Событие по закрытию окна.
		self.WindowOpen = 0

	def window_close(self):	# Закрытие окна.
		self.root.destroy()

class _SelectorIndicator:
	def __init__(self, root, Name, x, y):
		self.x = x
		self.y = y
		self.w = 42
		self.h = 42
		self.Name = Name
		self.StartColor = "#d0d0d0"
		self.OffColor = "#c0c0c0"
		self.OnColor = "#00bb00"
		self.Font = "Verdana 16 bold"

		# Холст.
		self.Box = Canvas(root, width = self.w, height = self.h, bg = BackGroundColor, bd = 0, highlightthickness = 0, relief = 'ridge')
		self.Box.place(x = self.x, y = self.y)
		# Круг
		self.Oval = self.Box.create_oval(0, 0, self.w - 1, self.h - 1, width = 2, fill = self.StartColor)
		# Название.
		self.Box.create_text(self.w / 2, self.h // 2, font = self.Font, justify = CENTER, fill = 'black', text = self.Name)
	def update(self, Value):
		if Value > 0:
			self.Box.itemconfig(self.Oval, fill = self.OnColor)
		else:
			self.Box.itemconfig(self.Oval, fill = self.OffColor)

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
		self.Font = "Verdana 12 bold"

		# Холст.
		self.Box = Canvas(root, width = self.w, height = self.h, bg = BackGroundColor, bd = 0, highlightthickness = 0, relief = 'ridge')
		self.Box.place(x = self.x, y = self.y)
		# Круг
		self.Oval = self.Box.create_oval(0, 0, self.w - 1, self.h - 1, width = 2, fill = self.StartColor)
		# Название.
		self.Box.create_text(self.w / 2, self.h // 2, font = self.Font, justify = CENTER, fill = 'black', text = self.Name)
	def update(self, Value):
		if Value > 0:
			self.Box.itemconfig(self.Oval, fill = self.OnColor)
		else:
			self.Box.itemconfig(self.Oval, fill = self.OffColor)