# Beam Status Monitor

Something to monitor the APS beam status and write big changes to a Slack workspace.

## Dependencies

```console
pip3 install slack-api slack-sdk pyepics
```

EPICS repeater:

```console
export EPICS_CA_ADDR_LIST=164.54.212.49
```

API key:

```console
SLACK_BOT_TOKEN=xoxb-fixme-token python3 monitor.py
```
