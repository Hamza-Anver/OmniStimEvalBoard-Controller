#!/usr/bin/env python3
from nicegui import ui
import time
from .comport import COMPort
from typing import List


class Terminal:
    """
    Handles all GUI elements for the serial terminal, using a COMPort instance
    for serial operations.
    """

    def __init__(self, ui: ui, com: COMPort):
        self.ui = ui
        self.com = com

        # UI references
        self.port_select = None
        self.baudrate_select = None
        self.connect_button = None
        self.disconnect_button = None
        self.timestamp_checkbox = None
        self.autoscroll_checkbox = None
        self.msg_input = None
        self.terminal_area = None

        # Terminal buffer
        self.buffer: List[str] = []
        self.max_buffer_size = 1000

        # Schedule periodic tasks
        ui.timer(1.0, self._refresh_ports)

    def _serial_options(self):
        with self.ui.row().classes(
            "w-full lg:flex lg:items-center lg:gap-4"
        ):  # port controls
            self.port_select = ui.select(
                label="Port", options=self.com.list_ports()
            ).classes("w-full lg:w-1/4")
            self.baudrate_select = ui.select(
                label="Baudrate",
                options=[
                    300,
                    1200,
                    2400,
                    4800,
                    9600,
                    14400,
                    19200,
                    38400,
                    57600,
                    115200,
                ],
                value=115200,
            ).classes("w-full lg:w-1/4")
            self.connect_button = (
                ui.button("Connect", icon="link", color="green")
                .classes("w-full lg:w-1/5")
                .on_click(self._connect)
            )
            self.disconnect_button = (
                ui.button("Disconnect", icon="link_off", color="red")
                .classes("w-full lg:w-1/5")
                .on_click(self._disconnect)
            )

    def _terminal_area(self):
        # terminal output area
        self.terminal_area = ui.scroll_area().classes(
            "font-mono border-gray-500 border-2 rounded-md bg-black text-white p-0 h-96 overflow-y-scroll overflow-x-hidden"
        )

    def _serial_send_controls(self):
        # send controls + options
            with self.ui.row().classes("w-full flex flex-wrap lg:gap-4 mt-2"):
                self.msg_input = ui.input(placeholder="Type message...").classes("grow")
                ui.button(icon="send").classes("w-full lg:w-1/12").on_click(
                    self._on_send_click
                )
                ui.button("Clear").classes("w-full lg:w-1/12").on_click(
                    self._clear_buffer
                )
                with ui.row().classes("w-full lg:w-1/4 items-center gap-4"):
                    self.timestamp_checkbox = ui.checkbox("Show timestamps", value=True)
                    self.autoscroll_checkbox = ui.checkbox("Autoscroll", value=True)

    def set_ui(self):
        with self.ui.card().classes("w-full h-full"):  # full width/height
            ui.label("Terminal Output").classes("text-xl font-bold")
            self._serial_options()
            self._terminal_area()
            self._serial_send_controls()
            

    def _connect(self):
        port = self.port_select.value
        baud = int(self.baudrate_select.value)
        if port:
            try:
                self.com.connect(port, baud)
                ui.notification(f"Connected to {port}", color="green", duration=3)
            except Exception as e:
                ui.notification(f"Connection failed: {e}", color="red", duration=3)
        else:
            ui.notification("Select a port first", color="blue", duration=3)

    def _disconnect(self):
        self.com.disconnect()
        ui.notification("Disconnected", color="green", duration=3)

    def _refresh_ports(self):
        if not self.port_select:
            return
        
        # Refresh the list of available ports
        current = self.com.list_ports()
        
        # Check if there are any differences in the lists
        if set(current) == set(self.port_select.options):
            return
        
        # Notify port additions and removals
        added = [p for p in current if p not in self.port_select.options]
        removed = [p for p in self.port_select.options if p not in current]
        if added:
            ui.notification(f"Added ports: {', '.join(added)}", color="green", duration=3)
        if removed:
            ui.notification(f"Removed ports: {', '.join(removed)}", color="red", duration=3)
        
        self.port_select.options = current
        if self.port_select.value not in current:
            self.port_select.value = None

        self.port_select.update()

    def parse_serial_line(self, raw: str):
        # If disconnected then set UI appropriately
        if raw == "DISCONNECTED":
            return
        
        #Optional timestamp
        if self.timestamp_checkbox.value:
            ts = time.strftime("%H:%M:%S", time.localtime())
            line = f"[{ts}] {raw}"
        else:
            line = raw
        self.buffer.append(line)
        if len(self.buffer) > self.max_buffer_size:
            self.buffer.pop(0)
        self._update_terminal()

    def _update_terminal(self):
        self.terminal_area.clear()
        if(self.terminal_area):
            with self.terminal_area:
                for line in self.buffer:
                    ui.label(line).classes("text-white")
        if self.autoscroll_checkbox.value:
            self.terminal_area.scroll_to(percent=1.0)

    def _on_send_click(self):
        text = self.msg_input.value.strip()
        if text:
            try:
                self.com.send(text)
                self.buffer.append(f"> {text}")
                if len(self.buffer) > self.max_buffer_size:
                    self.buffer.pop(0)
                self._update_terminal()
            except Exception as e:
                ui.notification(f"Send error: {e}", color="red", duration=3)
            self.msg_input.set_value("")

    def _clear_buffer(self):
        self.buffer.clear()
        self._update_terminal()
