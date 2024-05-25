import traceback
from time import sleep

from figure.plotter import Plotter, DynamicPlot
from figure.window import MatplotlibFigureScrollableWindow

from __init__ import *

if __name__ == "__main__":        
    try:
        # writer.start()
        plots = []
        for reader in readers:
            reader.start()
        
        for conf in plot_confs:
            plot = DynamicPlot(**conf)
            plots.append(plot)
            
        plotter = Plotter(plots=plots, show=False)
        window = MatplotlibFigureScrollableWindow(plotter)
        
        while moonlight_reader.thread.is_alive():
            sleep(1)
        
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        # writer.terminate()
        for reader in readers:
            reader.terminate()
    
    except Exception as e:
        print(e)
        traceback.print_exc()
        print("some exception happened!")
        # writer.terminate()
        for reader in readers:
            reader.terminate()
    
    
    