from nicegui import ui
import typing

class APLLCard:
    def __init__(self, ui: ui, serial_send: typing.Callable):
        self.ui = ui
        self.serial_send = serial_send

        self.inputs = None

    def parse_serial_line(self, line: str):
        """
        Parses a line from the serial input and updates the UI accordingly.
        Line format e.g. "APLL: 1234"
        """
        if line.startswith('APLL:'):
            try:
                value = int(line.split(':')[1].strip())
                self.inputs['apll'].set_value(value)

                self.ui.notify(f"APLL value updated: {value}", type="info", position="bottom-right")

                self._update_inputs()

            except ValueError:
                print(f"Invalid APLL value: {line}")

    def set_apll(self):
        """
        Sets the APLL value from the input field.
        """
        try:
            value = int(self.inputs['apll'].value)
            self.serial_send(f'SET APLL {value}')
        except ValueError:
            print("Invalid APLL value")

    

    def get_apll(self):
        self.serial_send('GET APLL')


    def _update_inputs(self):
        """
        Updates the inputs with the current values.
        """
        for key, input in self.inputs.items():
            if hasattr(input, 'value'):
                input.set_value(input.value)

    def set_ui(self):
        self.ui.label("APLL").classes("text-xl font-bold")

        self.inputs ={
            'apll': self.ui.number(label='APLL', placeholder='APLL').classes('w-full').tooltip("APLL value"),
        }

        with self.ui.row().classes('w-full flex'):
            self.ui.button('Set APLL', on_click=self.set_apll).classes('grow').tooltip("Send APLL values over serial")
            self.ui.button('Get APLL', on_click= self.get_apll).classes('grow').tooltip("Gets current APLL values from serial")