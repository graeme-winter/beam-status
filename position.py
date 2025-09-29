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

bpm_x_mean = 0.0
bpm_x_sd = 0.0

bpm_y_mean = 0.0
bpm_y_sd = 0.0


def transmit(message, timestamp):
    ts = datetime.datetime.fromtimestamp(timestamp)
    try:
        response = client.chat_postMessage(
            channel="C09H79FD0R4",
            text=message,
        )
    except:
        pass


def callback(pvname, value, timestamp, **kwargs):
    global bpm_x, bpm_y, n_bpm_x, n_bpm_y, NN, bpm_x_mean, bpm_x_sd, bpm_y_mean, bpm_y_sd

    if pvname == "S24IDFE-XBPM:P1us:x":
        bpm_x[n_bpm_x % NN] = value
        n_bpm_x += 1

        if n_bpm_x < NN:
            return

        mean, sd = numpy.mean(bpm_x), numpy.sqrt(numpy.var(bpm_x))

        if abs(mean - bpm_x_mean) > THRESH and abs(sd - bpm_x_sd) > THRESH:
            transmit(f"X position unstable in µ, σ: {mean:.1f} {sd:.1f}", timestamp)
            bpm_x_mean = mean
            bpm_x_sd = sd
        elif abs(mean - bpm_x_mean) > THRESH:
            transmit(f"X position unstable in µ: {mean:.1f}", timestamp)
            bpm_x_mean = mean
        elif abs(sd - bpm_x_sd) > THRESH:
            transmit(f"X position unstable in σ: {sd:.1f}", timestamp)
            bpm_x_sd = sd

    elif pvname == "S24IDFE-XBPM:P1us:y":
        bpm_y[n_bpm_y % NN] = value
        n_bpm_y += 1

        if n_bpm_y < NN:
            return

        mean, sd = numpy.mean(bpm_y), numpy.sqrt(numpy.var(bpm_y))

        if abs(mean - bpm_y_mean) > THRESH and abs(sd - bpm_y_sd) > THRESH:
            transmit(f"Y position unstable in µ, σ: {mean:.1f} {sd:.1f}", timestamp)
            bpm_y_mean = mean
            bpm_y_sd = sd
        elif abs(mean - bpm_y_mean) > THRESH:
            transmit(f"Y position unstable in µ: {mean:.1f}", timestamp)
            bpm_y_mean = mean
        elif abs(sd - bpm_y_sd) > THRESH:
            transmit(f"Y position unstable in σ: {sd:.1f}", timestamp)
            bpm_y_sd = sd


epics.camonitor("S24IDFE-XBPM:P1us:x", callback=callback)
epics.camonitor("S24IDFE-XBPM:P1us:y", callback=callback)

transmit(
    "Monitoring S24IDFE-XBPM:P1us:x and S24IDFE-XBPM:P1us:y", timestamp=time.time()
)

while True:
    time.sleep(1)
