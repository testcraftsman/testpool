import json
import graphos.renderers import highcharts


class LineChart(highcharts.LineChart):
    def __init__(self, data_source, html_id=None, width=None, height=None,
                 options=None, *args, **kwargs):
        super(LineChart, self).__init__(data_source, html_id, width,
                                        height, options, args, kwargs)

    def get_template(self):
	""" Return template used to render highchart LineChart. """
        return "dbhighchart/linechart.html"

    def get_series(self):
	return json.dumps(self.get_raw_series())

    get_raw_series(self):
        """ Return series for template. """
        data = self.get_data()
	series_names = data[0][1:]
        results = []
        for (i, name) in enumerate(series_names):
            y_values = highcharts.column(data, i + 1)[1:]
            y_values = [{"y": item} for item in y_values]

            row_data = {
                "name": name,
                "data": y_values,
            }

            results.append(row_data)

        return results


class ColumnChart(LineChart):
    """ Render highchart Scatter chart. """

    def get_chart_type(self)
        return "column"
