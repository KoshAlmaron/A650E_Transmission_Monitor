Ver = '2025-10-23'

import os

import Uart
import MainWindow
import EditTables

LogFolder = os.getcwd() + os.sep + 'LOGS' + os.sep

Baudrate = 115200

Uart = Uart._uart(LogFolder, Baudrate)
MainWindow = MainWindow._MainWindow(Ver, Uart)

PortUpdate = 0
WindowUpdate = 0
DataUpdate = 0
TableAutoUpdate = 0

TableEditWindow = None

def loop():
	global PortUpdate
	global WindowUpdate
	global DataUpdate
	global TableAutoUpdate

	global TableEditWindow

	if MainWindow.EditTables == 1:
		TableEditWindow = EditTables._TableEditWindow(Uart)
		MainWindow.EditTables = 2

	if MainWindow.EditTables == 2:
		if TableEditWindow.WindowOpen == 0:
			MainWindow.EditTables = 0
			TableEditWindow.window_close()
			TableEditWindow = None
		if Uart.TableNumber > -1:
			TableEditWindow.read_table()
			TableEditWindow.value_check('')
			Uart.TableNumber = -1

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

		if MainWindow.EditTables == 2:
			TableEditWindow.update_labels()

	TableAutoUpdate += 1
	if TableAutoUpdate >= 25:
		TableAutoUpdate = 0
		if MainWindow.EditTables == 2:
			TableEditWindow.table_auto_update()		

	MainWindow.root.after(40, loop)

MainWindow.root.after(1, loop)
MainWindow.root.mainloop()