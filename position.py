import datetime
import os
import time

import numpy

import epics

from slack_sdk import WebClient

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

NN = 100
THRESH = 1.0

bpm_x = numpy.zeros(shape=(NN,), dtype=numpy.float32)
bpm_y = numpy.zeros(shape=(NN,), dtype=numpy.float32)
n_bpm_x = 0
n_bpm_y = 0
old_current = 0


def transmit(message, timestamp):
    ts = datetime.datetime.fromtimestamp(timestamp)
    try:
        response = client.chat_postMessage(
            channel="C09HT6YUVED",
            text=message,
        )
    except:
        pass


def current(pvname, value, timestamp, **kwargs):
    global old_current
    ts = datetime.datetime.fromtimestamp(timestamp)
    if abs(value - old_current) < 5:
        return
    old_current = value
    try:
        response = client.chat_postMessage(
            channel="C09HT6YUVED",
            text=f"Beam current at {ts.strftime("%Y-%m-%d %H:%M:%S")}: {value:.1f}mA",
        )
    except:
        pass


def callback(pvname, value, timestamp, **kwargs):
    global bpm_x, bpm_y, n_bpm_x, n_bpm_y, NN

    # ignore BPMs if current < 10mA
    if old_current < 10:
        return

    if pvname == "S24IDFE-XBPM:P1us:x":
        bpm_x[n_bpm_x % NN] = value
        n_bpm_x += 1

        if n_bpm_x < NN:
            return

        sd = numpy.sqrt(numpy.var(bpm_x))

        if sd > THRESH:
            transmit(f"X position unstable in σ: {sd:.1f}", timestamp)

    elif pvname == "S24IDFE-XBPM:P1us:y":
        bpm_y[n_bpm_y % NN] = value
        n_bpm_y += 1

        if n_bpm_y < NN:
            return

        sd = numpy.sqrt(numpy.var(bpm_y))

        if sd > THRESH:
            transmit(f"Y position unstable in σ: {sd:.1f}", timestamp)


epics.camonitor("S24IDFE-XBPM:P1us:x", callback=callback)
epics.camonitor("S24IDFE-XBPM:P1us:y", callback=callback)
epics.camonitor("S-DCCT:CurrentM", callback=current, monitor_delta=10)


transmit(
    "Monitoring S-DCCT:CurrentM, S24IDFE-XBPM:P1us:x and S24IDFE-XBPM:P1us:y",
    timestamp=time.time(),
)

while True:
    time.sleep(100)
