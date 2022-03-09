from tkinter import *


class Redirect:
    def __init__(self, widget, autoscroll=True):
        self.widget = widget
        self.autoscroll = autoscroll

    def write(self, text):
        try:
            self.widget.insert('end', text)
            if self.autoscroll:
                self.widget.see("end")  # autoscroll
        except AttributeError:
            pass
