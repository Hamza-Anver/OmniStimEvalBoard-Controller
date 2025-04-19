from nicegui import ui

class ChartCard:
    def __init__(self, ui: ui):
        self.ui = ui
        self.data = {
            'time': [0],
            'value': [0]
        }

        self.chart_option = {
            'tooltip': {'trigger': 'axis'},
            'xAxis': {
                'type': 'category',
                'data': self.data['time'],
                'name': 'time (s)'
            },
            'yAxis': {
                'type': 'value',
                'name': 'value'
            },
            'series': [
                {
                    'name': 'value',
                    'type': 'line',
                    'data': self.data['value'],
                    'smooth': True
                }
            ]
        }
        self.data_min = None
        self.data_max = None
        self.ui_chart = None
        self.ui_polling_interval = None
        # 500 ms default polling interval
        self.polling_interval_ms = 500

        self.poll_data_loop()
        

    def poll_data_loop(self):
        """
        Poll data from the ADC and update the chart.
        This is a placeholder for the actual data polling logic.
        """
        # Simulate data polling
        self.data['time'].append(self.data['time'][-1] + 1)
        self.data['value'].append((self.data['value'][-1]+1)%10)

        if(len(self.data['time']) > 50):
            # Remove the oldest data point
            self.data['time'].pop(0)
            self.data['value'].pop(0)

        self.chart_option = {
            'tooltip': {'trigger': 'axis'},
            'xAxis': {
                'type': 'category',
                'data': self.data['time'],
                'name': 'time (s)'
            },
            'yAxis': {
                'type': 'value',
                'name': 'value'
            },
            'series': [
                {
                    'name': 'value',
                    'type': 'line',
                    'data': self.data['value'],
                    'smooth': False
                }
            ]
        }

        # Update chart with new data
        self.update_chart()

        # Update min/max labels
        if self.data_min and self.data_max:
            self.data_min.text = f"Min: {min(self.data['value'])}"
            self.data_max.text = f"Max: {max(self.data['value'])}"
            self.data_min.update()
            self.data_max.update()

        # Update polling interval
        if self.ui_polling_interval:
            self.polling_interval_ms = self.ui_polling_interval.value

        # Schedule the next poll
        self.ui.timer(self.polling_interval_ms/1000, self.poll_data_loop, once=True)


    def update_chart(self):
        """
        Update the chart with new data.
        This is a placeholder for the actual chart update logic.
        """
        if self.ui_chart:
            # Update the chart with new data
            self.ui_chart.options["series"][0]["data"] = self.data['value']
            self.ui_chart.options["xAxis"]["data"] = self.data['time']

            # Refresh the chart
            self.ui_chart.update()

    def set_ui(self):
        # Outer card, full width
        with self.ui.card().classes('w-full flex flex-col overflow-hidden'):
            self.ui.label('ADC Chart').classes('text-xl font-bold')
            with self.ui.row().classes('w-full items-center'):
                # Left pane: polling interval + min/max
                with self.ui.column().classes('w-2/12'):
                    self.ui_polling_interval = self.ui.number(
                    'Polling interval (ms)',
                    value=1000,
                    min=100,
                    max=5000,
                    step=100
                    ).classes('w-full')
                    self.data_min = self.ui.label("Min: N/A").classes('mt-2')
                    self.data_max = self.ui.label("Max: N/A").classes('mt-1')

                # Right pane: dummy line chart
                with self.ui.column().classes('grow'):
                    self.ui_chart = self.ui.echart(self.chart_option).classes('w-full')
                    
