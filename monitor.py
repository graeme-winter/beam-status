import datetime
import os
import time

import epics

from slack_sdk import WebClient

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

oldvalue = 0.0


def callback(pvname, value, timestamp, **kwargs):
    global oldvalue
    ts = datetime.datetime.fromtimestamp(timestamp)
    if abs(value - oldvalue) < 5:
        return
    oldvalue = value
    try:
        response = client.chat_postMessage(
            channel="C09HT6YUVED",
            text=f"Beam current at {ts.strftime("%Y-%m-%d %H:%M:%S")}: {value:.1f}mA",
        )
    except:
        pass


epics.camonitor("S-DCCT:CurrentM", callback=callback, monitor_delta=10)

while 1:
    time.sleep(100)
