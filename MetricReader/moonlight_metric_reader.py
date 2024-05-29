from time import sleep
from MetricReader.reader import Reader

from enum import Enum

from Util.data_parser import Parser

class MoonlightMetricReader(Reader):
    """A superclass of Reader that read moonlight overlay performance metric.
    """
    class MetricID(Enum):
        """Metric ID of Moonlight Metric
        """
        VIDEO_STREAM_RES = 0
        VIDEO_STREAM_FPS = 1
        INCOMING_FRAME_RATE = 2
        DECODING_FRAME_RATE = 3
        RENDERING_FRAME_RATE = 4
        MIN_PROCESSING_LATENCY = 5
        MAX_PROCESSING_LATENCY = 6
        AVERAGE_PROCESSING_LATENCY = 7
        FRAME_DROPPED_BY_NETWORK = 8
        FRAME_DROPPED_BY_JITTER = 9
        AVERAGE_NETWORK_LATENCY = 10
        AVERAGE_DECODING_TIME = 11
        AVERAGE_FRAME_QUEUE_DELAY = 12
        AVERAGE_RENDERING_TIME = 13
    
    def parse_args(self, filename="log.txt", **kwargs):
        super().parse_args(**kwargs)
        self._filename = filename
    
    def run(self):
        with open(self._filename, "r", encoding="utf8") as f:
            data = ""
            while not self._terminate:                
                while (read := f.readline()) != "\n" and not self._terminate:
                    data += read
                    # sys.stdout.write(read)
                    
                if self._terminate:
                    break
                
                # print("finished reading data. parsing!")
                # print(data)
                    
                parsed_metric = Parser.parse(data)
                
                if parsed_metric is None:
                    continue
                
                quant_metric = Parser.get_list_number_metric(parsed_metric)
                
                self._curr_value = quant_metric
                
                sleep(self._poll_rate)
                
                data = ""
        