class Parser():
    @staticmethod
    def parse(text):
        if text == "" or text == "\n":
            return None
        
        """Text format
            Video stream: [Resolution] [FPS] FPS (Codec: [Codec])
            Incoming frame rate from network: [FPS] FPS
            Decoding frame rate: [FPS] FPS
            Rendering frame rate: [FPS] FPS
            Host processing latency min/max/average: [min]/[max]/[avg] ms
            Frames dropped by your network connection: [jitter]%
            Frames dropped due to network jitter: [dropped]%
            Average network latency: [latency] ms (variance: 0 ms)
            Average decoding time: [latency] ms
            Average frame queue delay: [latencty] ms
            Average rendering time (including monitor V-sync latency): [rendering time] ms
        """
        
        parameter_metrics = text.split("\n")[:-1]
        
        parsed_metric = {}
        
        for parameter in parameter_metrics:
            split_parameter = parameter.split(":", 1)
            
            metric_name = split_parameter[0]
            metric = split_parameter[1].split(" ")[1:] # the 0th index is an empty string
            
            parsed_metric[metric_name] = metric
            
        return parsed_metric
    
   
    @staticmethod
    def get_list_number_metric(parsed_metric : dict):
        """
            Return a list of quantitative metric from parsed metric dictionary.
            The list contains data as follows:
            [
                0: video_stream_resolution
                1: video_stream_fps (in FPS)
                2: incoming frame rate from network (in FPS)
                3: Decoding frame rate (in FPS)
                4: Rendering frame rate (in FPS)
                5: Min processing latency (in ms)
                6: Max processing latency (in ms)
                7: Average processing latency (in ms)
                8: Frame dropped by network connection (in %)
                9: Frame dropped by jitter (in %)
                10: Average network latency (in ms)
                11: Average decoding time (in ms)
                12: Average frame queue delay (in ms)
                13: Average rendering time (in ms)
            ]         
        """
       
        ret = [-1 for i in range(15)]
       
        # Check if video stream entry is in the metric
        if (x := parsed_metric.get("Video stream", None)) is not None:
            ret[0] = x[0]
            ret[1] = x[1]
            
        
        if (x := parsed_metric.get("Incoming frame rate from network", None)) is not None:
            ret[2] = x[0]
            
        if (x := parsed_metric.get("Decoding frame rate", None)) is not None:
            ret[3] = x[0]
            
        if (x := parsed_metric.get("Rendering frame rate", None)) is not None:
            ret[4] = x[0]
            
        if (x := parsed_metric.get("Host processing latency min/max/average", None)) is not None:
            mma = x[0].split("/")
            
            ret[5] = mma[0]
            ret[6] = mma[1]
            ret[7] = mma[2]
            
        if (x := parsed_metric.get("Frames dropped by your network connection", None)) is not None:
            ret[8] = x[0][:-1]
            
        if (x := parsed_metric.get("Frames dropped due to network jitter", None)) is not None:
            ret[9] = x[0][:-1]
            
        if (x := parsed_metric.get("Average network latency", None)) is not None:
            ret[10] = x[0]
            
        if (x := parsed_metric.get("Average decoding time", None)) is not None:
            ret[11] = x[0]
        if (x := parsed_metric.get("Average frame queue delay", None)) is not None:
            ret[12] = x[0]
            
        if (x := parsed_metric.get("Average rendering time (including monitor V-sync latency)", None)) is not None:
            ret[13] = x[0]
            
        
        # return [
        #     parsed_metric["Video stream"][0],
        #     parsed_metric["Video stream"][1],
        #     parsed_metric["Incoming frame rate from network"][0],
        #     parsed_metric["Decoding frame rate"][0],
        #     parsed_metric["Rendering frame rate"][0],
        #     *parsed_metric["Host processing latency min/max/average"][0].split("/"),
        #     parsed_metric["Frames dropped by your network connection"][0][:-1], # remove the percentage
        #     parsed_metric["Frames dropped due to network jitter"][0][:-1],
        #     parsed_metric["Average network latency"][0],
        #     parsed_metric["Average decoding time"][0],
        #     parsed_metric["Average frame queue delay"][0],
        #     parsed_metric["Average rendering time (including monitor V-sync latency)"][0],
        # ]
        
        
        return ret
        
        
if __name__ == "__main__":
    text = """Video stream: 1920x1080 12.32 FPS (Codec: HEVC)
Incoming frame rate from network: 12.32 FPS
Decoding frame rate: 12.32 FPS
Rendering frame rate: 12.32 FPS
Host processing latency min/max/average: 1.4/1.8/1.6 ms
Frames dropped by your network connection: 0.00%
Frames dropped due to network jitter: 0.00%
Average network latency: 1 ms (variance: 0 ms)
Average decoding time: 0.00 ms
Average frame queue delay: 0.33 ms
Average rendering time (including monitor V-sync latency): 0.26 ms"""
    
    parsed_metric = Parser.parse(text)
    print(parsed_metric)
    
    metric = Parser.get_list_number_metric(parsed_metric)
    print(metric)
        
            
        
        
        
        