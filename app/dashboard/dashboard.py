from nicegui import ui
from .adcchart import ChartCard
import typing

class Dashboard:
    def __init__(self, ui: ui,  serial_send: typing.Callable, register_serial_cb: typing.Callable):
        self.chart_card = ChartCard(ui=ui, port_send=serial_send)
        register_serial_cb(self.chart_card.parse_serial_line)


    def set_ui(self):
        self.chart_card.set_ui()
        
