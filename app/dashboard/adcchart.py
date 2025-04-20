from nicegui import ui
import time
import typing


class ChartCard:
    def __init__(self, ui: ui, port_send: typing.Callable):
        self.ui = ui
        self.data = {"time": [0], "value": [0]}

        self.port_send = port_send
        self.card_title = None

        self.start_time_ns = time.time_ns()

        self.chart_option = {
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "data": self.data["time"],
                "name": "time (ms)",
            },
            "yAxis": {
                "type": "value",
                "name": "voltage (ADC)",
            },
            "series": [
                {
                    "name": "value",
                    "type": "line",
                    "data": self.data["value"],
                    "smooth": False,
                }
            ],
        }
        self.data_min = None
        self.data_max = None
        self.ui_chart = None
        self.data_params_table = None
        self.ui_polling_interval = None
        # 500 ms default polling interval
        self.polling_interval_ms = 500

        self.poll_data_loop()

    def poll_data_loop(self):
        """
        Poll data from the ADC and update the chart.
        This is a placeholder for the actual data polling logic.
        """
        # Call function to send command to MCU
        self.port_send("GET ADC")

        # Update polling interval
        if self.ui_polling_interval:
            self.polling_interval_ms = self.ui_polling_interval.value

        # Schedule the next poll
        try:
            self.ui.timer(self.polling_interval_ms / 1000, self.poll_data_loop, once=True)
        except Exception as e:
            self.ui.notify(f"Error scheduling polling: {e}", type="negative", position="bottom-right")
            # Use one second as a fallback
            self.ui.timer(1, self.poll_data_loop, once=True)

    def parse_serial_line(self, line: str):
        """
        Parse a line of data from the ADC.
        This is a placeholder for the actual parsing logic.
        """
        # Example parsing logic
        try:
            # Line format example: "ADC: 1234"
            if line.startswith("ADC"):
                value = int(line.split(":")[1].strip())
                self.data["value"].append(value)
                self.data["time"].append(
                    (time.time_ns() - self.start_time_ns) / 1_000_000
                )

                if len(self.data["time"]) > 50:
                    # Remove the oldest data point
                    self.data["time"].pop(0)
                    self.data["value"].pop(0)

                # Update chart with new data
                self.update_chart()

                # Update min/max labels
                if self.data_params_table:
                    self.data_params_table.rows[0]["raw"] = min(self.data["value"])
                    self.data_params_table.rows[1]["raw"] = max(self.data["value"])
                    if len(self.data["value"]) > 10:
                        self.data_params_table.rows[2]["raw"] = (
                            sum(self.data["value"][-10:]) / 10
                        )
                    self.data_params_table.update()

        except ValueError:
            pass

    def update_chart(self):
        """
        Update the chart with new data.
        This is a placeholder for the actual chart update logic.
        """
        if self.ui_chart:
            # Update the chart with new data
            self.ui_chart.options["series"][0]["data"] = self.data["value"]
            self.ui_chart.options["xAxis"]["data"] = self.data["time"]

            # Refresh the chart
            self.ui_chart.update()

    def set_ui(self):
        self.ui.label("ADC Chart").classes("text-xl font-bold")
        with self.ui.row().classes("w-full flex"):
            # Left pane: polling interval + data
            with self.ui.column().classes("w-fit"):
                self.ui_polling_interval = self.ui.number(
                    "Polling interval (ms)", value=1000, min=100, max=5000, step=100, validation="int"
                ).classes("w-full")

                self.data_params_table = self.ui.table(
                    rows=[
                        {"param": "Min", "raw": "N/A"},
                        {"param": "Max", "raw": "N/A"},
                        {"param": "Avg (last 10)", "raw": "N/A"},
                    ],
                    columns=[
                        {
                            "label": "Parameter",
                            "field": "param",
                            "align": "left",
                        },
                        {
                            "label": "Raw Value",
                            "field": "raw",
                            "align": "right",
                        },
                    ],
                ).classes("w-full")

            # Right pane: line chart
            with self.ui.column().classes("grow border border-black rounded-md"):
                self.ui_chart = self.ui.echart(self.chart_option)
