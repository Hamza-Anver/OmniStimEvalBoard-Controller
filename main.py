#!/usr/bin/env python3
from nicegui import ui

from app.terminal.comport import COMPort
from app.terminal.terminaltab import Terminal
from app.dashboard.adcchart import ChartCard

ui.page_title("OmniStim")

comport = COMPort()
term_tab = Terminal(ui=ui, com=comport)
chart_card = ChartCard(ui=ui)

def dash_tab():
    with ui.card().style('background-color: #f0f0f0').classes('w-full h-full'):
        ui.label('Dashboard content goes here.')

with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between p-0'):
    ui.label('OmniStim Controller').classes('text-2xl text-white m-3')
    with ui.tabs().classes('m-0 p-0') as tabs:
        dashboard = ui.tab('Dashboard', icon='multiline_chart')
        calculator = ui.tab('Calculator', icon='calculate')
        terminal = ui.tab('Terminal', icon='terminal')
        info = ui.tab('Info', icon='info')


with ui.tab_panels(tabs, value=dashboard).classes('w-full h-full'):
    with ui.tab_panel(dashboard):
        chart_card.chart_card()
    with ui.tab_panel(calculator):
        ui.label('Calculator content goes here.')
    with ui.tab_panel(terminal):
        term_tab.set_ui()
    with ui.tab_panel(info):
        ui.label('Info content goes here.')


with ui.footer(elevated=True).style('background-color: #737475').classes('items-center justify-between text-align-center'):
    ui.label('For the OmniStim Eval Board, made by Hamza Anver').classes('text-sm text-white')

ui.run()
