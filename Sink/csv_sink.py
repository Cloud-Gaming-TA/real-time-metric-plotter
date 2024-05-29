from Sink.sink import Sink


class CSVSink(Sink):
    def __init__(self, out_file: str, header, interval: float = 1) -> None:
        super().__init__(out_file, interval)
        
        header = list(map(lambda x: x.lower().replace(" ", "_"), header))
        self.header = header
        self._mapper = {}
        self._leftover = None
        
        for i, header in enumerate(self.header):
            self._mapper[header] = i
            
        self.csv_header = ",".join(self.header)
        
        
        with open(out_file, "w") as f:
            f.write(self.csv_header)
            f.write("\n")
           
    def save(self, line):
        if line == None:
            return
        
        with open(self._out_file, "a") as f:
            f.write(line)
            f.write("\n")
            
    def do_job(self, n_job):
        i = 0
        while i < n_job:    
            i, csv_string = self._parse(n_job)
            
            if i == -1:
                break
            
            self.save(csv_string)
    
    @staticmethod
    def format_empty_data(data):
        for i in range(len(data)):
            data[i] = "" if data[i] == None else data[i]
                        
        
    def _parse(self, n_job : int) -> tuple[int, str]:
        cursor = 0
        
        data = [None for i in range(len(self.header))]
        n_fill = 0
        
        while cursor < n_job:
            if n_fill == len(self.header):
                return cursor, ",".join(data)
            
            value = self.job.get()
            
            if value == None:
                return -1, None
            
            if (i := self._mapper.get(value.get("name", "").lower().replace(" ", "_"), None)) is not None:
                # data per line need to be sequentially ordered
                # which means when encouter the same header
                # end current line
                if data[i] != None:
                    self.format_empty_data(data)
                    return cursor, ",".join(data)
                
                data[i] = str(value.get("value", ""))
                n_fill += 1
                
            cursor += 1
        
        # cursor exceed the n_job and cursor == n_job
        self._leftover = data
        return cursor, None