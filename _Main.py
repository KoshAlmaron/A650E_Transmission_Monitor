Ver = '2026-01-14'

import os

import Uart
import MainWindow
import EditTables
import EditADC
import EditSpeed
import EditConfig
import PortState

import DataExport

LogFolder = os.getcwd() + os.sep + 'LOGS' + os.sep

Baudrate = 115200

Uart = Uart._uart(LogFolder, Baudrate)
MainWindow = MainWindow._MainWindow(Ver, Uart)

PortUpdate = 0
WindowUpdate = 0
DataUpdate = 0
TableAutoUpdate = 0

EditWindow = None
WindowState = 0

def loop():
	global PortUpdate
	global WindowUpdate
	global DataUpdate
	global TableAutoUpdate

	global EditWindow

	if MainWindow.EditTables == 1:
		MainWindow.EditTables = 0
		close_window(EditWindow)
		EditWindow = EditTables._TableEditWindow(Uart)
	if MainWindow.EditADC == 1:
		MainWindow.EditADC = 0
		close_window(EditWindow)
		EditWindow = EditADC._ADCEditWindow(Uart)
	if MainWindow.EditSpeed == 1:
		MainWindow.EditSpeed = 0
		close_window(EditWindow)
		EditWindow = EditSpeed._SpeedEditWindow(Uart)
	if MainWindow.EditConfig == 1:
		MainWindow.EditConfig = 0
		close_window(EditWindow)
		EditWindow = EditConfig._ConfigEditWindow(Uart)
	if MainWindow.DataExport == 1:
		MainWindow.DataExport = 0
		close_window(EditWindow)
		EditWindow = DataExport._DataExportEditWindow(Uart, Ver)
	if MainWindow.PortState == 1:
		MainWindow.PortState = 0
		close_window(EditWindow)
		EditWindow = PortState._PortStateEditWindow(Uart)

	if EditWindow is not None:
		if Uart.NewPortState == 1:
			if hasattr(EditWindow, 'update_port_state'):
				EditWindow.update_port_state()
			Uart.NewPortState = 0

		if EditWindow.WindowOpen == 0:
			EditWindow.window_close()
			EditWindow = None
		else:
			if EditWindow.WindowName == 'EditConfig':
				if Uart.NewConfig == 1:
					EditWindow.read_config()
					Uart.NewConfig = 0
			else:
				if Uart.TableNumber > -1:
					if hasattr(EditWindow, 'read_table'):
						EditWindow.read_table()
						Uart.TableNumber = -1
					if hasattr(EditWindow, 'value_check'):
						EditWindow.value_check('')

	if Uart.NewData == 1:
		MainWindow.update_graph_data()
		Uart.NewData = 0

	PortUpdate += 1
	if PortUpdate >= 25:
		PortUpdate = 0
		MainWindow.port_update()

	WindowUpdate += 1
	if WindowUpdate >= 4:
		WindowUpdate = 0
		MainWindow.update()

		if EditWindow is not None:
			if hasattr(EditWindow, 'update_data'):
				EditWindow.update_data()

	TableAutoUpdate += 1
	if TableAutoUpdate >= 25:
		TableAutoUpdate = 0
		if EditWindow is not None:
			if hasattr(EditWindow, 'table_auto_update'):
				EditWindow.table_auto_update()
			if hasattr(EditWindow, 'get_port_packet'):
				EditWindow.get_port_packet()

	MainWindow.root.after(40, loop)

def close_window(EditWindow):
	if EditWindow is not None:
		EditWindow.window_close()
		ADCEditWindow = None

MainWindow.root.after(1, loop)
MainWindow.root.mainloop()
