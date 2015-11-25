#!/usr/bin/python
import sys
import os
import salt.client


def getNotification():
    notification_dict = {}
    isEndOfDictionary = False
    for line in sys.stdin:
        if not line.strip():
            isEndOfDictionary = True
            continue
        if isEndOfDictionary:
            break
        key, value = line.split(':')
        notification_dict[key] = value.lstrip()[:-1]
    return notification_dict, line


def postTheNotificationToSaltMaster():
    salt_payload = {}
    threshold_dict = {}
    caller = salt.client.Caller()
    threshold_dict['tags'], threshold_dict['message'] = getNotification()
    tag = "skyring/collectd/node/{0}/threshold/{1}/{2}".format(
        threshold_dict['tags']["Host"],
        threshold_dict['tags']["Plugin"],
        threshold_dict['tags']["Severity"])
    caller.sminion.functions['event.send'](tag, threshold_dict)


if __name__ == '__main__':
    postTheNotificationToSaltMaster()
