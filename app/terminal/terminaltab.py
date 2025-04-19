#!/usr/bin/env python3
from nicegui import ui
import serial
from typing import Optional, List, Dict, Any
import serial.tools.list_ports


class Terminal:
    def __init__(self, ui: ui) -> None:
        self.ui = ui
        self.port_select = None
        self.port_select_options: List[str] = []

        self.baudrate_select = None
        self.baudrate_select_options: List[int] = [
            300,
            1200,
            2400,
            4800,
            9600,
            14400,
            19200,
            38400,
            57600,
            115200
        ]
        self.serial = None
        

        ui.timer(1.0, self.auto_update)

    def auto_update(self) -> None:
        if self.port_select:
            # If there is a change in available ports, update the select options
            current_ports = self.get_ports()
            if set(current_ports) != set(self.port_select_options):
                # Update the select options
                self.port_select.options = current_ports
                self.port_select.update()
                if self.port_select.value not in self.port_select_options:
                    self.port_select.value = None

                # Figure out if ports have been added or removed
                added_ports = set(current_ports) - set(self.port_select_options)
                removed_ports = set(self.port_select_options) - set(current_ports)

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
                self.port_select_options = current_ports

    def get_ports(self) -> List[str]:
        ports = serial.tools.list_ports.comports()
        list_ports = [port.device for port in ports]
        # print(f"Available ports: {self.port_select_options}")
        return list_ports

    def term_tab(self) -> None:
        with self.ui.row():
            self.port_select = ui.select(label="Port", options=[]).classes("w-64")
            self.baudrate_select = ui.select(label="Baudrate", options=self.baudrate_select_options, value=115200).classes("w-64")
                
            
