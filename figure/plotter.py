import numpy as np

import matplotlib.axes
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from MetricReader.reader import Reader

class DynamicPlot():
    def __init__(self, metrics : list[dict] = [], sink : Reader = None, max_points : int = 100, title="", ylim : tuple = None, xlabel : str = "", ylabel : str = "", bg : str ="#ffffff", color : str = "#1f77b4") -> None:
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

        if not issubclass(type(sink), Reader):
            raise ValueError("sink must be a subclass of", Reader)
        
        self._sink = sink
        
        self._ax = None
        
        self._last_value = [0 for i in range(len(metrics))]
        
        
    def add_point(self, i, point):
        self.data[i] = np.roll(self.data[i], -1)
        self.data[i][-1] = point
        
    def set_sink(self, sink):
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
        
        if self._sink.get() is None or self._sink.get()[metric["metric_id"]] == -1:
            self.add_point(i, self._last_value[i])
        else: 
            self.add_point(i, self._sink.get()[metric["metric_id"]])
            self._last_value[i] = float(self._sink.get()[metric["metric_id"]])
        
        print(f"{self.title}-{metric.get('metric_id')}: {self._last_value[i]}")
        
        if self._last_value[i] > self.ylim[1]:
            self.ylim = (self.ylim[0], self._last_value[i])
            self._ax.set_ylim(0, 1.5 * self._last_value[i])
            self._ax.set_yticks(np.round(np.linspace(*self._ax.get_ylim(), 5)))
            self._ax.figure.canvas.draw()

        self.lines[i].set_ydata(self.data[i])
        
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
    
    def __init__(self, plots : list[DynamicPlot], show=True):
        self.plots = plots
        self._show = show
        self.fig, self.axs = plt.subplots(len(self.plots) // 2 + len(self.plots) % 2, 2, figsize=(10, 4 * (len(self.plots) // 2 + len(self.plots) % 2)), layout="constrained")
        # plt.subplots_adjust(bottom=2)
        
        self._ani = None

        for i, plot in enumerate(self.plots):
            row = i // 2
            col = i % 2
            plot.set_axis(self.axs[row, col])
            
        if len(self.plots) % 2 != 0:
            self.fig.delaxes(self.axs[-1, -1])
        
        if self._show:
            self.fig.tight_layout()

            
    def update(self, _=0):
        print("Update period start")
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


