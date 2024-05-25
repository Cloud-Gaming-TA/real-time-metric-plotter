from threading import Thread
from multiprocessing import Value
from MetricReader.reader import Reader

import psutil
from scapy.all import sniff, ifaces

class ProcessNetworkMonitor():
    def __init__(self, proc : list[psutil.Process]):
        self._proc = proc
        self._net = {}
        self._all_macs = {iface.mac for iface in ifaces.values()}
        
        self.set_process_port()
        
        # Force close thread when all thread are stopped  
        # thanks to: https://blog.skyplabs.net/posts/python-sniffing-inside-thread/  
        self.thread = Thread(target=self.run, daemon=True)
        
        self.net_usage = [0, 0] # in bytes
        self._terminate = False
    
    def set_process_port(self):
        for _proc in self._proc:
            for pconn in _proc.connections():
                if pconn.status == "ESTABLISHED":
                    self._net[(pconn.laddr.port, pconn.raddr.port)] = True
                    self._net[(pconn.raddr.port, pconn.laddr.port)] = True
                    
    def start(self):
        self._terminate = False
        self.thread.start()
    
    def should_sniff_stop(self, packet):
        return self._terminate
    
    def terminate(self, timeout=None):
        self._terminate = True
        self.thread.join(timeout)
    
    def process_packet(self, packet):
        try:
            packet_connection =  (packet.sport, packet.dport)
        except (AttributeError, IndexError):
            pass
        
        else:
            # Check if the packet correspond to the process
            is_process_packet = self._net.get(packet_connection, False)
            
            if is_process_packet:
                if packet.src in self._all_macs:
                    self.net_usage[1] += len(packet)
                    
                else:
                    self.net_usage[0] += len(packet)

    def run(self):
        sniff(iface="Wi-Fi", prn=self.process_packet, store=False, stop_filter=self.should_sniff_stop)
            
        
        
class ProcessMetricReader(Reader):
    """Read CPU Usage, Memory Usage, and Network Usage of a process. 
    """
    
    # network usgae monitoring per process
    # is thansk to this blog post : https://thepythoncode.com/article/make-a-network-usage-monitor-in-python
    
    
    class MetricID():
        CPU_USAGE = 0
        MEMORY = 1
        SENT_BYTES = 2
        DOWNLOAD_SPEED = 3
        RECEIVE_BYTES = 4
        UPLOAD_SPEED = 5
    
    @staticmethod
    def _read_cpu_usge(procs, interval):
        percent = Value("d")
        
        def read(proc):
            p = proc.cpu_percent(interval)
            with percent.get_lock():
                percent.value += p
                
        t = []
        
        for _proc in procs:
            _t = Thread(target=read, args=(_proc, ))
            _t.start()
            t.append(_t)
            
        for thread in t:
            thread.join()
            
        return percent.value
    
    @staticmethod
    def _read_mem_usgae(procs):
        mem = 0
        for _proc in procs:
            mem += _proc.memory_info().rss / (1024 ** 2)
            
        return mem
            
    def parse_args(self, process_name="", **kwargs):
        if process_name == "":
            raise ValueError("process name is an empty string. ProcessMetricReader must be initialized with a process_name")
        
        self._process_name = process_name
        self._proc = []
        
        # Search for the process 
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            if proc.info['name'] == self._process_name:
                print(f"Found process {process_name}. the process has pid : {proc.pid}")
                self._proc.append(proc)
            
        
        if len(self._proc) == 0:
            raise ValueError(f"process {process_name} is not running")
        
        
        
        self._net_sniffer = ProcessNetworkMonitor(self._proc)
        self._net_sniffer.start()
            
        # self._pconn = (self._proc.connections()[0].laddr, self._proc.connections()[0].raddr)
        
        return super().parse_args(**kwargs)
    
    def run(self):
        data = [-1, -1, 0, 0, 0, 0]
        while not self._terminate:
            # this will block / pause the reader (equal with sleep)
            data[self.MetricID.CPU_USAGE] = self._read_cpu_usge(self._proc, self._poll_rate)
            data[self.MetricID.MEMORY] = self._read_mem_usgae(self._proc)
            data[self.MetricID.DOWNLOAD_SPEED] = (self._net_sniffer.net_usage[0] - data[self.MetricID.RECEIVE_BYTES]) / self._poll_rate / 1024
            data[self.MetricID.UPLOAD_SPEED] = (self._net_sniffer.net_usage[1] - data[self.MetricID.SENT_BYTES]) / self._poll_rate / 1024
            data[self.MetricID.RECEIVE_BYTES] = self._net_sniffer.net_usage[0] / 1024
            data[self.MetricID.SENT_BYTES] = self._net_sniffer.net_usage[1] / 1024
            self._curr_value = data
            
            # recalculate the port of the process to see if new
            # connection is open
            self._net_sniffer.set_process_port()
            
    def terminate(self):
        super().terminate()
        print("Trying to stop sniffer")
        self._net_sniffer.terminate(2)
        
        if self._net_sniffer.thread.is_alive():
            print("Force terminate sniffer thread")