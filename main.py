#!/usr/bin/env python3
from nicegui import ui

from app.terminal.comport import COMPort
from app.terminal.terminalcard import Terminal
from app.dashboard.dashboard import Dashboard

ui.page_title("OmniStim")

comport = COMPort()
term_tab = Terminal(ui=ui, com=comport)
dashboard_tab = Dashboard(ui=ui, serial_send=comport.send, register_serial_cb=comport.register_callback)

comport.register_callback(term_tab.parse_serial_line)

ui.timer(0.01, comport.read_serial, once=False)

with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between p-0'):
    ui.label('OmniStim Controller').classes('text-2xl text-white m-3')
    with ui.tabs().classes('m-0 p-0') as tabs:
        dashboard = ui.tab('Dashboard', icon='multiline_chart')
        calculator = ui.tab('Calculator', icon='calculate')
        terminal = ui.tab('Terminal', icon='terminal')
        info = ui.tab('Info', icon='info')


with ui.tab_panels(tabs, value=dashboard).classes('w-full h-full'):
    with ui.tab_panel(dashboard):
        dashboard_tab.set_ui()
    with ui.tab_panel(calculator):
        ui.label('Calculator content goes here.')
    with ui.tab_panel(terminal):
        term_tab.set_ui()
    with ui.tab_panel(info):
        ui.label('Info content goes here.')


with ui.footer(elevated=True).style('background-color: #737475').classes('items-center justify-between text-align-center'):
    ui.label('For the OmniStim Eval Board, made by Hamza Anver').classes('text-sm text-white')

ui.run()
