from nicegui import ui
from .adcchart import ChartCard
from .daccard import DACCard
from .apllcard import APLLCard
import typing

class Dashboard:
    def __init__(self, ui: ui,  serial_send: typing.Callable, register_serial_cb: typing.Callable):
        self.ui = ui
        self.chart_card = ChartCard(ui=ui, port_send=serial_send)
        self.apll_card = APLLCard(ui=ui, serial_send=serial_send)
        self.dac_card = DACCard(ui=ui)
        register_serial_cb(self.chart_card.parse_serial_line)
        register_serial_cb(self.apll_card.parse_serial_line)


    def set_ui(self):
        with self.ui.card().classes("w-full"):
            self.chart_card.set_ui()
        
        with self.ui.row().classes("w-full flex"):

            with self.ui.card().classes("max-lg:w-full lg:grow"):
                self.apll_card.set_ui()
                
            with self.ui.card().classes("max-lg:w-full lg:grow"):
                self.dac_card.set_ui()

            

        
