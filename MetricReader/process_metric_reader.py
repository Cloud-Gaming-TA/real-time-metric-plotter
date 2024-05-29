from threading import Thread
from multiprocessing import Value
from MetricReader.reader import Reader

from enum import Enum

import psutil
from scapy.all import sniff, ifaces, conf

conf.use_pcap = True
conf.use_npcap = True


class ProcessNetworkMonitor():
    def __init__(self, proc : list[psutil.Process], adapter : str):
        print(adapter)
        self._adapter = adapter
        self._proc = proc
        self._net = {}
        self._all_macs = {iface.mac for iface in ifaces.values()}
        print(self._all_macs)
        
        self.set_process_port()
        
        # Force close thread when all thread are stopped  
        # thanks to: https://blog.skyplabs.net/posts/python-sniffing-inside-thread/  
        self.thread = Thread(target=self.run, daemon=True)
        
        self.net_usage = [0, 0] # in bytes
        self._terminate = False
    
    def set_process_port(self):
        for _proc in self._proc:
            try:
                for pconn in _proc.connections():
                        self._net[pconn.laddr.port] = True
            except psutil.NoSuchProcess:
                continue
                    
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
            if self._net.get(packet_connection[0], False):
                # upload
                self.net_usage[1] += len(packet) / (1024 ** (2))
                    
            elif self._net.get(packet_connection[1], False):
                # download
                self.net_usage[0] += len(packet) / (1024 ** (2))

    def run(self):
        sniff(iface=self._adapter, prn=self.process_packet, store=False, stop_filter=self.should_sniff_stop)
            
        
        
class ProcessMetricReader(Reader):
    """Read CPU Usage, Memory Usage, and Network Usage of a process. 
    """
    
    # network usgae monitoring per process
    # is thansk to this blog post : https://thepythoncode.com/article/make-a-network-usage-monitor-in-python
    
    
    class MetricID(Enum):
        CPU_USAGE = 0
        MEMORY = 1
        SENT_BYTES = 2
        DOWNLOAD_SPEED = 3
        RECEIVE_BYTES = 4
        UPLOAD_SPEED = 5
    
    def _maintain_process(self):
        for i, proc in enumerate(self._proc):
            if not proc.is_running():
                self._proc_pid[proc.pid] = False
                del self._proc[i]
                
        self._add_proc(self._process_name)
        
    @staticmethod
    def _read_cpu_usge(procs : list[psutil.Process], interval, no_process_callback):
        percent = Value("d")
        
        def read(proc):
            try:
                p = proc.cpu_percent(interval)
                with percent.get_lock():
                    percent.value += p
            except psutil.NoSuchProcess:
                no_process_callback()
                return
                
        t = []
        
        for _proc in procs:
            
            _t = Thread(target=read, args=(_proc, ), daemon=True)
            _t.start()
            t.append(_t)
            
        for thread in t:
            thread.join()
        
                    
        return percent.value
    
    @staticmethod
    def _read_mem_usgae(procs, no_process_callback):
        mem = 0
        for _proc in procs:
            try:
                mem += _proc.memory_info().rss / (1024 ** 2)
            except psutil.NoSuchProcess:
                no_process_callback()
                continue
            
        return mem
    
    
    def _add_proc(self, process_name, log=False):
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            if proc.info['name'] == self._process_name:
                if log:
                    print(f"Found process {process_name}. the process has pid : {proc.pid}")
                
                if not self._proc_pid.get(proc.pid, False):
                    # only add new pid proc
                    self._proc_pid[proc.pid] = True
                    self._proc.append(proc)
    
    def parse_args(self, process_name="", adapter_name="WI-FI", **kwargs):
        if process_name == "":
            raise ValueError("process name is an empty string. ProcessMetricReader must be initialized with a process_name")
        
        self._adapter_name = adapter_name
        self._process_name = process_name
        self._proc = []
        self._proc_pid = {}
        
        # Search for the process 
        self._add_proc(self._process_name, log=True)
            
        
        if len(self._proc) == 0:
            raise ValueError(f"process {process_name} is not running")
        
        
        
        self._net_sniffer = ProcessNetworkMonitor(self._proc, self._adapter_name)
        self._net_sniffer.start()
            
        # self._pconn = (self._proc.connections()[0].laddr, self._proc.connections()[0].raddr)
        
        return super().parse_args(**kwargs)
    
    def run(self):
        data = [-1, -1, 0, 0, 0, 0]
        while not self._terminate:
            # Maintain the process 
            # self._maintain_process()
            # self._add_proc(self._process_name)
            
            # this will block / pause the reader (equal with sleep)
            data[self.MetricID.CPU_USAGE.value] = self._read_cpu_usge(self._proc, self._poll_rate, self._maintain_process) / psutil.cpu_count()
            data[self.MetricID.MEMORY.value] = self._read_mem_usgae(self._proc, self._maintain_process)
            data[self.MetricID.DOWNLOAD_SPEED.value] = (self._net_sniffer.net_usage[0] - data[self.MetricID.RECEIVE_BYTES.value]) / self._poll_rate
            data[self.MetricID.UPLOAD_SPEED.value] = (self._net_sniffer.net_usage[1] - data[self.MetricID.SENT_BYTES.value]) / self._poll_rate 
            data[self.MetricID.RECEIVE_BYTES.value] = self._net_sniffer.net_usage[0]
            data[self.MetricID.SENT_BYTES.value] = self._net_sniffer.net_usage[1]
                       
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