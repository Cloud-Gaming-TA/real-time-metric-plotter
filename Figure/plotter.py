from enum import Enum
from datetime import datetime

import numpy as np

import matplotlib.axes
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from MetricReader.reader import Reader
from Sink.sink import Sink
from Sink.csv_sink import CSVSink

class DynamicPlot():
    def __init__(self, metrics : list[dict] = [], source : Reader = None, max_points : int = 100, title="", ylim : tuple = None, xlabel : str = "", ylabel : str = "", bg : str ="#ffffff", color : str = "#1f77b4") -> None:
        self.max_points = max_points
        self.lines = [None for i in range(len(metrics))]
        self.data = [None for i in range(len(metrics))]
        
        self.color = color
        self.bg = bg
        
        
        self.metrics = metrics
        
        self.ylabel = ylabel
        self.xlabel = xlabel
        
        self.ylim = ylim

        self.title = title

        if not issubclass(type(source), Reader):
            raise ValueError("source must be a subclass of", Reader)
        
        self._source = source
        self._sink = None
        
        self._ax = None
        
        self._last_value = [0 for i in range(len(metrics))]
        
    def get_metric_name(self):
        res = []
        for metric in self.metrics:
            res.append(metric["metric_id"].name)
        
        return res
    
    def add_point(self, i, point):
        self.data[i] = np.roll(self.data[i], -1)
        self.data[i][-1] = point
        
    def set_source(self, source):
        self._source = source
    
    def set_sink(self, sink : Sink):
        self._sink = sink
        
    def set_axis(self, ax):
        self._ax : matplotlib.axes.Axes = ax
        
        activate_legend  = False
        
        for (i, metric) in enumerate(self.metrics):
            if (label := metric.get("label", "")) != "":
                activate_legend = True
                
            self.data[i] = np.zeros(self.max_points)
            line, = self._ax.plot(self.data[i], label=label, color=metric.get("color", "##1f77b4"))
            self.lines[i] = line
        
        if activate_legend:
            self._ax.legend()
            
        self._ax.set_xticklabels([])
        
        self._ax.set_ylim(self.ylim)
        self._ax.set_xlabel(self.xlabel)
        self._ax.set_title(self.title)
        self._ax.set_facecolor(self.bg)
        
        
    def update(self, _=0):
        for i, metric in enumerate(self.metrics):
            self._update_per_metric(i, metric, _)
            
        return self.lines
    
    def _update_per_metric(self, i, metric : dict, _=0):
        # Due to the unblocking nature of this function design
        # on each update cyle, the data that are captured
        # are either, constant (update cycle > point update cyle)
        # or missing some point (update cycle < point update cycle)
        # point gen can use some somoothing function to improve
        # plotting accuracy
        
        metric_id = metric["metric_id"]
        
        if self._source.get() is None or self._source.get()[metric_id.value] == -1:
            self.add_point(i, self._last_value[i])
        else: 
            self.add_point(i, self._source.get()[metric_id.value])
            self._last_value[i] = float(self._source.get()[metric_id.value])
                
        if self._last_value[i] > self.ylim[1]:
            self.ylim = (self.ylim[0], self._last_value[i])
            self._ax.set_ylim(0, 1.5 * self._last_value[i])
            self._ax.set_yticks(np.round(np.linspace(*self._ax.get_ylim(), 5)))
            self._ax.figure.canvas.draw()

        self.lines[i].set_ydata(self.data[i])
        
        if self._sink != None:
            self._sink.add_job({
                "name": metric_id.name,
                "value": self._last_value[i]
            })
            
        # if self._last_value > self.ylim[1]:
        #     self._ax.set_ylim((self.ylim[0], self._last_value * 2))
        #     self._ax.autoscale_view()
    
        # elif self._last_value < self.ylim[0]:
            
        #     if (self._last_value < 0):
        #         self._ax.set_ylim((self._last_value * 2, self.ylim[1]))
        #     else:
        #         self._ax.set_ylim((0, self.ylim[1]))
                
        #     self._ax.autoscale_view()
           

class Plotter():
    INTERVAL = 100
    SINK_CSV_OUTPUT_PATH = f"out/plot/csv/{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    class SinkType(Enum):
        CSV = "csv"
        TEXT = "text"
        
    def __init__(self, plots : list[DynamicPlot], sink_type : SinkType = None, show=True):
        self.sink_type = sink_type
        self.plots = plots
        
        if self.sink_type == self.SinkType.CSV:
            header = []
            
            for plot in self.plots:
                header.extend(plot.get_metric_name())
            
            import pathlib
            pathlib.Path('out/plot/csv').mkdir(parents=True, exist_ok=True) 
            self._sink = CSVSink(self.SINK_CSV_OUTPUT_PATH, header=header)
            self._sink.start()
            
        else:
            self._sink = None
            
        self._show = show
        self.fig, self.axs = plt.subplots(len(self.plots) // 2 + len(self.plots) % 2, 2, figsize=(10, 4 * (len(self.plots) // 2 + len(self.plots) % 2)), layout="constrained")
        # plt.subplots_adjust(bottom=2)
        
        self._ani = None

        for i, plot in enumerate(self.plots):
            row = i // 2
            col = i % 2
            plot.set_axis(self.axs[row, col])
            plot.set_sink(self._sink)
            
        if len(self.plots) % 2 != 0:
            self.fig.delaxes(self.axs[-1, -1])
        
        if self._show:
            self.fig.tight_layout()

    
    def terminate_sink(self):
        print("trying to terminate sink")
        if self._sink != None:
            self._sink.terminate()
        print("sink has been terminated gracefully")
        
    def update(self, _=0):
        # print("Update period start")
        lines = []
        for plot in self.plots:
            lines.extend(plot.update(_))
        return lines

    def animate(self, fig=None):
        if fig is None:
            fig = self.fig
                
        self.ani = animation.FuncAnimation(fig, self.update, interval=self.INTERVAL, blit=True)
        
        if self._show:
            plt.show()


