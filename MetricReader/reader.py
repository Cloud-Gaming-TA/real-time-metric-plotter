from abc import ABC, abstractmethod
import threading

class Reader(ABC):
    """Reader Abstract class. This class is responsible on
    reading data (polling) on some metric. The process is configured
    to run without blocking. 
"""
    DEFAULT_POLL_RATE_S = 0.1
     
    class MetricID():
        pass
     
    def parse_args(self, **kwargs):
        # Use current class default rate
        self._poll_rate = kwargs.get("poll_rate", self.DEFAULT_POLL_RATE_S)
        return
    
    def __init__(self, **kwargs):
        self._curr_value : list[str] = None
        self.thread = threading.Thread(target=self.run)
        self._terminate = True
        self.parse_args(**kwargs)
    
    def start(self):
        if self._terminate:
            print("Thread is already running!")
            
        self._terminate = False
        self.thread.start()

    @abstractmethod
    def run(self):
        pass
        
    def terminate(self):
        self._terminate = True
        self.thread.join()
    
    
    def get(self) -> list[str]:
        """Return a list of metric. Each metric is identified with it's ID. When reader hasn't read any data (the first time), 
        None will be returned. Reader can also read partial data, if a data isn't available after reading, -1 will be 
        stored as the value of the metric that are missing. 
        
        Returns:
            list[str] : list of metric
        """
        return self._curr_value
    
    def get_from_metric_id(self, metric_id : int) -> str:
        """return metric of metric_id

        Args:
            metric_id (int): the id of the metric

        Returns:
            str : the metric value
        """
        
        return self._curr_value[metric_id]