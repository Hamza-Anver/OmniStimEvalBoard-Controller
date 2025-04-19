#!/usr/bin/env python3
from nicegui import ui
import serial
import serial.tools.list_ports
import time
from typing import List


class Terminal:
    """
    Terminal UI component for serial communication using NiceGUI,
    with optional timestamps and autoscroll.
    """

    def __init__(self, ui: ui) -> None:
        # UI references
        self.ui = ui
        self.port_select = None
        self.baudrate_select = None
        self.connect_button = None
        self.disconnect_button = None
        self.timestamp_checkbox = None
        self.autoscroll_checkbox = None
        self.msg_input = None

        # Serial and port settings
        self.serial = None
        self.port_options: List[str] = []
        self.baudrate_options: List[int] = [
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
        ]

        # Terminal buffer
        self.buffer: List[str] = []
        self.max_buffer_size: int = 1000

        #callbacks
        self.callbacks: List[callable] = []

        # Element ID for scrolling
        self.terminal_window_scroll_area = None

        # Start periodic tasks
        ui.timer(1.0, self._refresh_ports)
        ui.timer(0.01, self._read_serial)

    def _list_ports(self) -> List[str]:
        return [p.device for p in serial.tools.list_ports.comports()]

    def _refresh_ports(self) -> None:
        current = self._list_ports()
        if set(current) != set(self.port_options):
            self.port_select.options = current
            new = set(current) - set(self.port_options)
            missing = set(self.port_options) - set(current)
            if new:
                ui.notification(
                    f"New port: {', '.join(new)}", color="green", duration=3
                )
            if missing:
                ui.notification(
                    f"Port removed: {', '.join(missing)}", color="red", duration=3
                )
            self.port_options = current
            if self.port_select.value not in current:
                self.port_select.value = None

    def connect(self) -> None:
        if self.port_select.value:
            try:
                self.serial = serial.Serial(
                    self.port_select.value, int(self.baudrate_select.value)
                )
                ui.notification(
                    f"Connected to {self.port_select.value}", color="green", duration=3
                )
            except serial.SerialException as e:
                ui.notification(f"Connection failed: {e}", color="red", duration=3)
        else:
            ui.notification("Select a port first", color="blue", duration=3)

    def disconnect(self) -> None:
        if self.serial and self.serial.is_open:
            self.serial.close()
            ui.notification("Disconnected", color="green", duration=3)
        else:
            ui.notification("No active connection", color="blue", duration=3)

    def _read_serial(self) -> None:
        if self.serial and self.serial.is_open and self.serial.in_waiting:
            try:
                raw = self.serial.readline().decode("utf-8", errors="replace").strip()
                if raw:
                    # add optional timestamp
                    if self.timestamp_checkbox.value:
                        ts = time.strftime("%H:%M:%S", time.localtime())
                        line = f"[{ts}] {raw}"
                    else:
                        line = raw
                    self.buffer.append(line)
                    if len(self.buffer) > self.max_buffer_size:
                        self.buffer.pop(0)

                    # Call all registered callbacks
                    for callback in self.callbacks:
                        callback(line)
                        
                    # Update the terminal display
                    self._update_terminal()
            except Exception as e:
                ui.notification(f"Read error: {e}", color="red", duration=3)

    def send(self, text: str) -> None:
        if self.serial and self.serial.is_open:
            try:
                self.serial.write((text + "\n").encode("utf-8"))
                self.buffer.append(f"> {text}")
                if len(self.buffer) > self.max_buffer_size:
                    self.buffer.pop(0)
                self._update_terminal()
            except Exception as e:
                ui.notification(f"Send error: {e}", color="red", duration=3)
        else:
            ui.notification("Not connected", color="blue", duration=3)

    def append_callback(self, callback: callable) -> None:
        """
        Append a callback function to the list of callbacks.
        This function is called when new data is received from the serial port.
        """
        self.callbacks.append(callback)


    def _update_terminal(self) -> None:
        if self.terminal_window_scroll_area:
            # Add labels to scroll area
            with self.terminal_window_scroll_area as scroll_area:
                scroll_area.clear()
                for line in self.buffer[-self.max_buffer_size :]:
                    ui.label(line).classes("text-sm")

            # autoscroll if enabled
            if self.autoscroll_checkbox.value:
                self.terminal_window_scroll_area.scroll_to(percent=1.0)

    def _on_send_click(self) -> None:
        text = self.msg_input.value.strip()
        if text:
            self.send(text)
            self.msg_input.set_value("")

    def term_tab(self) -> None:
        with self.ui.card().classes("w-full h-full"):
            ui.label("Terminal Output").classes("text-lg font-bold")
            with self.ui.row().classes("w-full"):
                self.port_select = ui.select(
                    label="Port", options=self._list_ports()
                ).classes("w-full lg:w-1/4")
                self.baudrate_select = ui.select(
                    label="Baudrate", options=self.baudrate_options, value=115200
                ).classes("w-full lg:w-1/4")
                self.connect_button = (
                    ui.button("Connect", icon="link", color="green")
                    .classes("w-full lg:w-1/5")
                    .on_click(self.connect)
                )
                self.disconnect_button = (
                    ui.button("Disconnect", icon="link_off", color="red")
                    .classes("w-full lg:w-1/5")
                    .on_click(self.disconnect)
                )
                
            self.terminal_window_scroll_area = ui.scroll_area().classes(
                "font-mono outline-none border-gray-500 border-2 rounded-md bg-black text-white p-2 h-96 overflow-y-auto overflow-x-hidden"
            )

            with self.ui.row().classes("mt-2 w-full"):
                self.msg_input = ui.input(placeholder="Type message...").classes("w-full lg:w-1/4 ")
                ui.button(icon="send").on_click(self._on_send_click).classes("w-full lg:w-2/12")
                ui.button("Clear").on_click(
                    lambda: self.buffer.clear() or self._update_terminal()
                ).classes("w-full lg:w-2/12")
                self.timestamp_checkbox = ui.checkbox("Show timestamps", value=True).classes("w-1/2 lg:w-2/12")
                self.autoscroll_checkbox = ui.checkbox("Autoscroll", value=True).classes("w-1/2 lg:w-2/12")
