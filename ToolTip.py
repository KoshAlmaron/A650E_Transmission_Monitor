from tkinter import *
from tkinter import ttk

class ToolTip:
	def __init__(self, Widget, Text):
		self.Widget = Widget
		self.Text = Text
		self.ShowDelay = 500

		self.ToolTipLabel = None
		self.Focus = 0
		self.Widget.bind("<Enter>", self.show_after)
		self.Widget.bind("<Leave>", self.hide)

	def show_after(self, event):
		self.Focus = 1
		self.Widget.after(self.ShowDelay, self.show)

	def show(self):
		if self.Focus and self.ToolTipLabel == None:
			#print('Show')

			DeltaY = len(self.Text.split('\n')) * 25 

			x = self.Widget.winfo_rootx() + self.Widget.winfo_reqwidth()
			y = self.Widget.winfo_rooty() #- DeltaY

			self.ToolTipLabel = Toplevel(self.Widget)
			self.ToolTipLabel.wm_overrideredirect(True)
			self.ToolTipLabel.wm_geometry(f"+{x}+{y}")

			W = 400 # Ширина окна подсказки.

			Label = ttk.Label(self.ToolTipLabel, text = self.Text, background = "#ffffe0", relief = "solid", borderwidth = 1, font = "Verdana 14", padding = 5, wraplength = W)
			Label.pack()

	def hide(self, event=None):
		#print('Hide')
		self.Focus = 0
		if self.ToolTipLabel:
			#print('Destroy')
			self.ToolTipLabel.destroy()
			self.ToolTipLabel = None
