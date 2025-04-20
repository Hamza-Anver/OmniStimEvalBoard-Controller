from nicegui import ui
import typing

class DACCard:
    def __init__(self, ui: ui):
        self.ui = ui

    def set_ui(self):
        self.ui.label("DAC").classes("text-xl font-bold")