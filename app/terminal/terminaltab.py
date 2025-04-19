#!/usr/bin/env python3
from nicegui import ui
import serial
from typing import Optional, List, Dict, Any
import serial.tools.list_ports


class Terminal:
    def __init__(self, ui: ui) -> None:
        self.ui = ui
        self.port_select = None
        self.baudrate = None
        self.serial = None
        self.available_ports: List[str] = []

        ui.timer(1.0, self.auto_update)

    def auto_update(self) -> None:
        if self.port_select:
            # If there is a change in available ports, update the select options
            current_ports = self.get_ports()
            if set(current_ports) != set(self.available_ports):
                # Update the select options
                self.port_select.options = current_ports
                self.port_select.update()
                if self.port_select.value not in self.available_ports:
                    self.port_select.value = None

                # Figure out if ports have been added or removed
                added_ports = set(current_ports) - set(self.available_ports)
                removed_ports = set(self.available_ports) - set(current_ports)

                # Notify the user about added or removed ports
                if added_ports:
                    ui.notification(
                        f"New COM Port: {', '.join(added_ports)}",
                        color="green",
                        duration=3,
                    )

                if removed_ports:
                    ui.notification(
                        f"COM Port Disconnected: {', '.join(removed_ports)}",
                        color="red",
                        duration=3,
                    )

                # Update the available ports
                self.available_ports = current_ports

    def get_ports(self) -> List[str]:
        ports = serial.tools.list_ports.comports()
        list_ports = [port.device for port in ports]
        # print(f"Available ports: {self.available_ports}")
        return list_ports

    def term_tab(self) -> None:
        with self.ui.row():
            self.available_ports = self.get_ports()
            self.port_select = ui.select(label="Port", options=self.available_ports).classes("w-64") 
