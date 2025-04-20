from nicegui import ui
import typing

class DACCard:
    def __init__(self, ui: ui):
        self.ui = ui

    def set_ui(self):
        self.ui.label("DAC").classes("text-xl font-bold")


        self.inputs ={
            'dac0': self.ui.number(label='DAC0', placeholder='DAC0').classes('w-full').tooltip("DAC A value (0-1023)"),
        }

        with self.ui.row().classes('w-full flex'):
            self.ui.button('Set DAC').classes('grow').tooltip("Send DAC values over serial")
            self.ui.button('Get DAC').classes('grow').tooltip("Gets current DAC values from serial")