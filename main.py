#!/usr/bin/env python3
from nicegui import ui

from app.terminal.terminaltab import Terminal

ui.page_title("OmniStim")

term_tab = Terminal(ui=ui)

def dash_tab():
    with ui.card().style('background-color: #f0f0f0').classes('w-full h-full'):
        ui.label('Dashboard content goes here.')

with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
    ui.label('OmniStim Controller').classes('text-2xl text-white')

with ui.footer(elevated=True).style('background-color: #737475').classes('items-center justify-between text-align-center'):
    ui.label('For the OmniStim Eval Board, made by Hamza Anver').classes('text-sm text-white')

with ui.splitter(value=30).classes('w-full max-w-lg h-full') as splitter:
    with splitter.before:
        with ui.tabs().props('vertical').classes('w-full') as tabs:
            dashboard = ui.tab('Dashboard', icon='multiline_chart')
            calculator = ui.tab('Calculator', icon='calculate')
            terminal = ui.tab('Terminal', icon='terminal')
            info = ui.tab('Info', icon='info')
    with splitter.after:
        with ui.tab_panels(tabs, value=dashboard) \
                .props('vertical').classes('w-full h-full'):
            with ui.tab_panel(dashboard):
                dash_tab()
            with ui.tab_panel(calculator):
                ui.label('Calculator content goes here.')
            with ui.tab_panel(terminal):
                term_tab.term_tab()
            with ui.tab_panel(info):
                ui.label('Info content goes here.')

ui.run()
