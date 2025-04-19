import serial
import serial.tools.list_ports
from typing import List, Callable


class COMPort:
    """
    Handles serial port operations: listing ports, connect, disconnect,
    sending data, reading data, and notifying registered callbacks.
    """
    def __init__(self):
        self.serial = None
        self.callbacks: List[Callable[[str], None]] = []

    def list_ports(self) -> List[str]:
        """Return a list of available serial port device names."""
        return [p.device for p in serial.tools.list_ports.comports()]

    def connect(self, port: str, baudrate: int) -> None:
        """Open the serial port at given baudrate."""
        if self.serial and self.serial.is_open:
            self.disconnect()
        self.serial = serial.Serial(port, baudrate)

    def disconnect(self) -> None:
        """Close the serial port if open."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.serial = None

    def send(self, text: str) -> None:
        """Send a line of text (with newline) over the serial port."""
        if self.serial and self.serial.is_open:
            self.serial.write((text + '\n').encode('utf-8'))
            # call callbacks with the sent text
            self._call_callbacks("SENT > " + text)

    def _call_callbacks(self, data: str) -> None:
        """
        Invoke all registered callbacks with the given data.
        This is a helper function to ensure that callbacks are called
        in a thread-safe manner.
        """
        for cb in self.callbacks:
            cb(data)

    def read_serial(self) -> None:
        """
        Read available data from the serial port. For each full line,
        invoke all registered callbacks with the decoded string.
        """
        if self.serial and self.serial.is_open and self.serial.in_waiting:
            try:
                raw = self.serial.readline().decode('utf-8', errors='replace').strip()
                if raw:
                    self._call_callbacks(raw)
            except Exception:
                pass
        else:
            try:
                self._call_callbacks("DISCONNECTED")
            except Exception:
                pass

    def register_callback(self, callback: Callable[[str], None]) -> None:
        """
        Register a function to be called whenever a new line is read.
        Callback signature: callback(line: str) -> None
        """
        self.callbacks.append(callback)
