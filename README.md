# Run
1. install the dependencies. I highly recommend to install this inside python virtual environment. You can go to this [link](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) for more details on how to create venv
```
pip install -r requirements.txt
```

2. Run
```
python main.py
```

If your python version >= 3.8 and using windows, then i think you are fine. Else, maybe there could be
some compatibility issues. 


# Adding metric to the plot
Modify the __init__.py file. 

Here is an example on adding a cpu usage from process_reader to the plot.
```python
plot_confs = [
  {
        "metrics": [
            {
                "metric_id": process_reader.MetricID.CPU_USAGE,
                "color" : "#3b3b3b"
            }
        ],
        
        "sink": process_reader,
        "title": "CPU Usage",
        "ylim": [0, 100],
        "ylabel": "Utiliaztion(%)"   
    },
]
```

# FAQ
## What is a metric_id?
the plot will get a metric from a Reader object. Each class that inherit from Reader will have an Object define on the class called MetricID that define the 
metric that this reader offers. As of now, there are two Reader available that you can add to the plot, MoonlightMetricReader and ProcessReader. 

## Is there format of the configurations that i can refer to?
Yes, it's inside the __init__.py file

## What is a source?
Source is the reader that offer the metric, make sure to instantinate the reader first. 

## Can you add a new source?
Yes, you can create a new reader class by inheriting from Reader class. 

## Can i save the data?
Yes, by default, plotter will save the plot data into a csv, located at ./out/plot/csv.


