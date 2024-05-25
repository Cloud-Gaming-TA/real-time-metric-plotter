# Run
1. install the dependencies
```
pip install -r requirements.txt
```

2. Run
```
python main.py
```


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

## What is a sink?
Sink is the reader that offer the metric, make sure to instantinate the reader first. 

## Can you add a new sink?
Yes, you can create a new reader class by inheriting from Reader class. 
