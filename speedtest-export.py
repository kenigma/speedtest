#!/usr/bin/python3

from prometheus_client import start_http_server, Gauge
import random
import time
import subprocess
import json
import threading
import sys

labels = ['server_name', 'server_id']
latencyGauge = Gauge('ping_latency', 'Ping Latency in ms', labels)
downloadGauge = Gauge('download_speed', 'Download speed in bytes', labels)
uploadGauge = Gauge('upload_speed', 'Upload speed in bytes', labels)
interval = 30 * 60   # 30 mins

# function to read 
def doSpeedtest(interval, latencyGauge, downloadGauge, uploadGauge):
    while(True):
        try:
            servers = [
                '13623',    # Singtel  
                '13538'     # CSL
            ]
            for id in servers:
                print("checking for server "+ id)
                comp = subprocess.run(['speedtest', '-s', id, '-f', 'json'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                output_str = comp.stdout
                res = json.loads(output_str)
                ping = res["ping"]["latency"]
                upload = res["upload"]["bandwidth"]
                download = res["download"]["bandwidth"]
                server_name = res["server"]["name"]
                print("Result for %s (%s): %d, %d, %d" % (id, server_name, ping, download, upload))
                latencyGauge.labels(server_name, id).set(ping)
                uploadGauge.labels(server_name, id).set(upload)
                downloadGauge.labels(server_name, id).set(download)
        except:
            print("Unexpected error doing speed test:", sys.exc_info()[0])
        # sleep before speed testing again
        time.sleep(interval)

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8008)
    try:
        t1 = threading.Thread(target = doSpeedtest, args = (interval, latencyGauge, downloadGauge, uploadGauge))
        t1.start()
        t1.join()
    except:
        print("Unexpected error creating thread: ", sys.exc_info()[0])
    #while True:
     #   time.sleep(10)
    