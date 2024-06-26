# Plotter configurations
from MetricReader.moonlight_metric_reader import MoonlightMetricReader
from MetricReader.process_metric_reader import ProcessMetricReader

############################# Define the reader here ##########################################

# Moonlight reader
# MOONLIGHT path to logs.txt
# located at [PATH_TO_MOONLIGHT_FOLDER_WHERE_MOONLIGHT.exe_RESIDE]/log.txt
FILENAME = "D:/Kerjaan/moonlight-custom/moonlight-qt/build/deploy-x64-release/log.txt" # absolute path
moonlight_reader = MoonlightMetricReader(filename=FILENAME)


# Procee reader
NET_ADAPTER = "Wi-Fi"
PROCESS_NAME="Spotify.exe"
process_reader = ProcessMetricReader(process_name=PROCESS_NAME, adapter_name=NET_ADAPTER, poll_rate=0.5)



# put all of the reader here
readers = [
    moonlight_reader, 
    process_reader,
]

# Matplotlib style
import matplotlib as mpl
mpl.rcParams["font.family"] = "Times New Roman"
mpl.style.use('seaborn-v0_8-deep')

"""Plot configuration
{
    "metrics" : [
        {
            "metric_id" : READER_CLASS.MetricID.METRIC_THAT_THE_PLOT_WILL_USE (Required)
            "label" : "the metric label" (Optional)
            "color" : "the color of the plot" (Optional)
        }
        ...
    ] (Required atleast 1)
    
    "source" : process_reader / reader / any subclass of Reader (Required)
    "maxpoint" : max_point on the axis (Optional)
    "title": "my plot" (Optional)
    "xlabel" : "time" (Optional)
    "ylabel" : "bytes" (Optional)
    "ylim" : (lower, upper) (Required)
    "bg" : "plot background color" (Optional)
}    
"""

# Define your plot here
plot_confs = [
    # Plot configuration
    {
        "metrics": [
            {
                "metric_id": process_reader.MetricID.CPU_USAGE,
                "color" : "#3b3b3b"
            }
        ],
        
        "source": process_reader,
        "title": "CPU Usage",
        "ylim": [0, 100],
        "ylabel": "Utiliaztion(%)"   
    },
    {
        "metrics": [
            {
                "metric_id": process_reader.MetricID.RECEIVE_BYTES,
                "label": "Receive Bytes",
                "color": "#3b2b4b"
            },
            {
                "metric_id": process_reader.MetricID.SENT_BYTES,
                "label": "Sent Bytes",
                "color": "#ff000a"
            }   
        ],
        "source": process_reader,
        "title": "Network Usage",
        "ylim": [0, 100],
        "ylabel": "Network Usage(in MiB)"
    },
    {
        "metrics": [
            {
                "metric_id": process_reader.MetricID.DOWNLOAD_SPEED,
                "label": "Download Speed",
                "color": "#3b2b4b"
            },
            {
                "metric_id": process_reader.MetricID.UPLOAD_SPEED,
                "label": "Upload Speed",
                "color": "#ff000a"
            }   
        ],
        "source": process_reader,
        "title": "Network Speed",
        "ylim": [0, 15],
        "ylabel": "Network Speed(in MiB/s)"
    },
    {
        "metrics": [
            {
                "metric_id": moonlight_reader.MetricID.VIDEO_STREAM_FPS,
                "color": "#2b2b2b"
            },
        ],
        "source": moonlight_reader,
        "title": "Video FPS",
        "ylim": [0, 60],
        "ylabel": "FPS"
    },
    {
        "metrics": [
            {
                "metric_id": moonlight_reader.MetricID.AVERAGE_NETWORK_LATENCY,
                "color": "#2b2b2b"
            },
        ],
        "source": moonlight_reader,
        "title": "Network Latency",
        "ylim": [0, 60],
        "ylabel": "Latency (ms)"
    }
]
    
