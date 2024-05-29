from threading import Thread
from time import sleep
from multiprocessing import Value, Queue
from abc import ABC, abstractmethod

class Sink(ABC):
    def __init__(self, out_file : str, interval : float = 1) -> None:
        self._out_file = out_file
        self._interval_time = interval
        self._terminate = False
        self.thread = Thread(target=self.run)
        self._n_job = Value("i", 0)
        self.job = Queue(maxsize=1000)
        
    def add_job(self, data : list[dict]):
        self.job.put(data)
        
        with self._n_job.get_lock():
            self._n_job.value += 1
    
    @abstractmethod
    def do_job(self, n_job):
        pass
    
    def start(self):
        if self.thread.is_alive():
            print("Thread is already running!")
            
        self._terminate = False
        self.thread.start()

    def terminate(self):
        self._terminate = True
        self.add_job(None)
        self.thread.join()

    def run(self):
        while not self._terminate:
            sleep(self._interval_time)
            
            print("Pipe output to sink")
            
            with self._n_job.get_lock():
                n_job = self._n_job.value
                self._n_job.value = 0
                
            self.do_job(n_job=n_job)