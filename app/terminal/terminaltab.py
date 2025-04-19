#!/usr/bin/env python3
from nicegui import ui
import serial
from typing import List
import serial.tools.list_ports
import asyncio

class Terminal:
    """
    Terminal UI component for serial communication using NiceGUI.
    """
    def __init__(self, ui: ui) -> None:
        # UI references
        self.ui = ui
        self.port_select = None
        self.baudrate_select = None
        self.connect_button = None
        self.disconnect_button = None
        self.terminal_window = None
        self.msg_input = None     # <-- new

        # Serial and port settings
        self.serial = None
        self.port_options: List[str] = []
        self.baudrate_options: List[int] = [300, 1200, 2400, 4800, 9600,
                                           14400, 19200, 38400, 57600, 115200]

        # Terminal buffer
        self.buffer: List[str] = []
        self.max_buffer_size: int = 1000

        # Start periodic tasks
        ui.timer(1.0, self._refresh_ports)
        # Can be adjusted to a lower value for more frequent checks
        ui.timer(0.01, self._read_serial)

    def _refresh_ports(self) -> None:
        """Detect changes in COM ports and update selection options."""
        current = self._list_ports()
        if set(current) != set(self.port_options):
            self.port_select.options = current
            missing = set(self.port_options) - set(current)
            new = set(current) - set(self.port_options)
            if new:
                ui.notification(f"New port: {', '.join(new)}", color='green', duration=3)
            if missing:
                ui.notification(f"Port removed: {', '.join(missing)}", color='red', duration=3)
            self.port_options = current
            if self.port_select.value not in current:
                self.port_select.value = None

    def _list_ports(self) -> List[str]:
        """Return list of available serial port device names."""
        return [p.device for p in serial.tools.list_ports.comports()]

    def connect(self) -> None:
        """Open serial connection to selected port and baudrate."""
        if self.port_select.value:
            try:
                self.serial = serial.Serial(self.port_select.value,
                                            int(self.baudrate_select.value))
                ui.notification(f"Connected to {self.port_select.value}", color='green', duration=3)
            except serial.SerialException as e:
                ui.notification(f"Connection failed: {e}", color='red', duration=3)
        else:
            ui.notification("Select a port first", color='blue', duration=3)

    def disconnect(self) -> None:
        """Close active serial connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            ui.notification("Disconnected", color='green', duration=3)
        else:
            ui.notification("No active connection", color='blue', duration=3)

    def _read_serial(self) -> None:
        """Read incoming data from serial and update terminal buffer."""
        if self.serial and self.serial.is_open and self.serial.in_waiting:
            try:
                line = self.serial.readline().decode('utf-8').strip()
                if line:
                    self.buffer.append(line)
                    if len(self.buffer) > self.max_buffer_size:
                        self.buffer.pop(0)
                    self._update_terminal()
            except Exception as e:
                ui.notification(f"Read error: {e}", color='red', duration=3)

    def send(self, text: str) -> None:
        """Send text to serial port and append to buffer."""
        if self.serial and self.serial.is_open:
            try:
                self.serial.write((text + '\n').encode('utf-8'))
                self.buffer.append(f"> {text}")
                if len(self.buffer) > self.max_buffer_size:
                    self.buffer.pop(0)
                self._update_terminal()
            except Exception as e:
                ui.notification(f"Send error: {e}", color='red', duration=3)
        else:
            ui.notification("Not connected", color='blue', duration=3)

    def _update_terminal(self) -> None:
        """Refresh terminal window display with current buffer."""
        if self.terminal_window:
            self.terminal_window.set_text("\n".join(self.buffer[-self.max_buffer_size:]))

    def _on_send_click(self) -> None:
        """Handler for Send button."""
        text = self.msg_input.value.strip()
        if text:
            self.send(text)
            self.msg_input.set_value('')  # clear input

    def term_tab(self) -> None:
        """Render the terminal UI components in a tab or container."""
        with self.ui.row():
            # Port and baudrate selectors
            self.port_select = ui.select(label='Port', options=self._list_ports()).classes('w-64')
            self.baudrate_select = ui.select(label='Baudrate',
                                             options=self.baudrate_options,
                                             value=115200).classes('w-64')
            # Connect/disconnect buttons
            self.connect_button = ui.button('Connect').classes('w-32').on_click(self.connect)
            self.disconnect_button = ui.button('Disconnect').classes('w-32').on_click(self.disconnect)

        # Terminal output area
        ui.label('Terminal Output').classes('text-lg font-bold')
        self.terminal_window = ui.label().classes('w-full h-64 overflow-auto bg-gray-100 p-2')
        self.terminal_window.style('white-space: pre-wrap; font-family: monospace;')

        # New: Message input + Send button
        with self.ui.row().classes('mt-2'):
            self.msg_input = ui.input(placeholder='Type message...').classes('w-3/4')
            ui.button('Send').classes('w-1/4').on_click(self._on_send_click)
