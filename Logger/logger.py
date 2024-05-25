import threading
from time import sleep

class Logger():
    INTERVAL = 5000
    def __init__(self, out_file = "log.txt") -> None:
        self._out_file = out_file
        self.thread = threading.Thread(target=self.run)
        self._terminate = False
        self._csv_out = {}
        self._counter = 0
    
    def terminate(self):
        self._terminate = True
        self.thread.join()
        
    def start(self):
        # Clear the output text
        open(self._out_file, "w").close()
        self.thread.start()
        
    def set_log_text(self, log):
        pass
    
    def set_log_csv(self, data, _type):
        if self._csv_out.get(_type, None) is None:
            self._csv_out[_type] = [data]
            return
        
        self._csv_out[_type].append(data)
            
    def write_csv_to_txt(self):
        
        

            
        
                

        