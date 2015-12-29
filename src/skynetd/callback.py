#
# Copyright 2015 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import inspect
import salt.config
from functools import wraps
from logger import logger
from constants import ONE_GB_IN_KB, SKYNET_CONF_FILE


cb_info = {
    "drive_add": {
        "bus_name": "org.storaged.Storaged",
        "signal_name": "InterfacesAdded",
        "path": None,
        "dbus_interface": "org.freedesktop.DBus.ObjectManager"
    },
    "drive_remove": {
        "bus_name": "org.storaged.Storaged",
        "signal_name": "InterfacesRemoved",
        "path": None,
        "dbus_interface": "org.freedesktop.DBus.ObjectManager"
    },
    "drive_corruption": {
        "bus_name": "org.storaged.Storaged",
        "signal_name": "PropertiesChanged",
        "path": None,
        "dbus_interface": "org.freedesktop.DBus.Properties"
    },
    "block_property_changed": {
        "bus_name": "org.storaged.Storaged",
        "signal_name": "PropertiesChanged",
        "path": None,
        "dbus_interface": "org.freedesktop.DBus.Properties"
    },
    "block_add": {
        "bus_name": "org.storaged.Storaged",
        "signal_name": "InterfacesAdded",
        "path": None,
        "dbus_interface": "org.freedesktop.DBus.ObjectManager"
    },
    "block_remove": {
        "bus_name": "org.storaged.Storaged",
        "signal_name": "InterfacesRemoved",
        "path": None,
        "dbus_interface": "org.freedesktop.DBus.ObjectManager"
    },
    "mount_state_change": {
        "bus_name": "org.storaged.Storaged",
        "signal_name": "PropertiesChanged",
        "path": None,
        "dbus_interface": "org.freedesktop.DBus.Properties"
    },
    "glusterd_status": {
        "signal_name": "PropertiesChanged",
        "path": "/org/freedesktop/systemd1/unit/glusterd_2eservice",
        "dbus_interface": "org.freedesktop.DBus.Properties",
        "bus_name": None
    },
    "salt_minion_status": {
        "signal_name": "PropertiesChanged",
        "path": "/org/freedesktop/systemd1/unit/salt_2dminion_2eservice",
        "dbus_interface": "org.freedesktop.DBus.Properties",
        "bus_name": None
    },
    "network_device_added": {
        "signal_name": "DeviceAdded",
        "path": "/org/freedesktop/NetworkManager",
        "dbus_interface": "org.freedesktop.NetworkManager",
        "bus_name": "org.freedesktop.NetworkManager"
    },
    "network_device_removed": {
        "signal_name": "DeviceRemoved",
        "path": "/org/freedesktop/NetworkManager",
        "dbus_interface": "org.freedesktop.NetworkManager",
        "bus_name": "org.freedesktop.NetworkManager"
    },
    "network_device_changed": {
        "signal_name": "PropertiesChanged",
        "path": None,
        "dbus_interface": "org.freedesktop.NetworkManager.Device.Wired",
        "bus_name": "org.freedesktop.NetworkManager"
    },
    "collectd_status": {
        "signal_name": "PropertiesChanged",
        "path": "/org/freedesktop/systemd1/unit/collectd_2eservice",
        "dbus_interface": "org.freedesktop.DBus.Properties",
        "bus_name": None
    },
    "lvm_vg_create": {
        "bus_name": "org.storaged.Storaged",
        "signal_name": "InterfacesAdded",
        "path": None,
        "dbus_interface": None
    },
    "lvm_vg_delete": {
        "bus_name": "org.storaged.Storaged",
        "signal_name": "InterfacesRemoved",
        "path": None,
        "dbus_interface": None
    },
    "lvm_lv_create": {
        "bus_name": "org.storaged.Storaged",
        "signal_name": "InterfacesAdded",
        "path": None,
        "dbus_interface": None
    },
    "lvm_lv_delete": {
        "bus_name": "org.storaged.Storaged",
        "signal_name": "InterfacesRemoved",
        "path": None,
        "dbus_interface": None
    }
}


def dbus_signal_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            res, tag = func(*args, **kwargs)
            if not res and not tag:
                return

            args[0].caller.sminion.functions['event.send'](
                tag,
                res
            )
            logger.debug("Event Pushed successfully - Handler: %s | Data: %s |"
                         " Tag: %s" % (func.func_name, str(res), str(tag)))
        except Exception as e:
            logger.error("Error in handler: %s | Reason: %s | Args: %s |"
                         " Kwargs: %s" % (func.func_name, str(e),
                                          str(args), str(kwargs)))
    return wrapper


class Callback(object):
    """
    Call back class that contains all the callback functions.
    """
    def __init__(self, caller):
        self.caller = caller
        try:
            self.minion_id = salt.config.minion_config(
                '/etc/salt/minion')['id']
        except Exception as e:
            logger.error("Could not get the salt minion id: %s", str(e))

    @dbus_signal_handler
    def drive_add(self, a, d, path):
        for k, v in d.iteritems():
            if k.split('.')[-1] == "Drive":
                res = {}
                res["tags"] = {}
                res["tags"]["ID"] = str(v.get("Id"))
                res["tags"]["size"] = str(v.get("Size"))
                res["tags"]["Model"] = str(v.get("Model"))
                res["tags"]["Seat"] = str(v.get("Seat"))
                res["tags"]["Serial"] = str(v.get("Serial"))
                res["tags"]["Vendor"] = str(v.get("Vendor"))
                res["message"] = "New storage drive of size %s Gb added"\
                                 " Id: %s" % (str(
                                     float(res["tags"]["size"])/(ONE_GB_IN_KB)
                                 ), res["tags"]["ID"])
                res["severity"] = "INFO"
                tag = "dbus/node/{0}/generic/storage/drive/added".format(
                    self.minion_id)
                return res, tag

    @dbus_signal_handler
    def drive_remove(self, a, d, path):
        for e in d:
            if e.split('.')[-1] == "Drive":
                res = {}
                res["tags"] = {}
                res["tags"]["ID"] = str(a.split('/')[-1]).replace("_", "-")
                res["tags"]["Action"] = "Removed"
                res["message"] = "Storage drive Removed ID: %s" % (
                    res["tags"]["ID"])
                res["severity"] = "Warning"
                tag = "dbus/node/{0}/generic/storage/drive/removed".format(
                    self.minion_id)
                return res, tag

    @dbus_signal_handler
    def drive_corruption(self, a, d, c, path):
        res = {}
        res["tags"] = {}
        device_id = path.split("/")[-1]
        if a.split('.')[-1] == "Ata":
            for k, v in d.items():
                if k in ["SmartFailing", "SmartTemperature",
                         "SmartSelftestStatus", "SmartNumAttributesFailing"]:
                    res["tags"][str(k)] = str(v)

            if not res:
                return None, None
            res["tags"]["deviceId"] = device_id
            res["message"] = "Device with id: %s might be failing" % (
                device_id)
            res["severity"] = "Critical"
            tag = "dbus/node/{0}/generic/storage/drive/possible"\
                  "Failure".format(self.minion_id)
            return res, tag

    @dbus_signal_handler
    def block_property_changed(self, a, d, c, path):
        res = {}
        res["tags"] = {}
        device_name = path.split("/")[-1]
        if a.split('.')[-1] == "Block":
            for k, v in d.items():
                if k in ["IdType", "IdUsage", "IdVersion"]:
                    res["tags"][str(k)] = str(v)

            if not res:
                return None, None
            res["tags"]["deviceName"] = device_name
            res["message"] = "Properties of block device %s has changed" % (
                device_name)
            res["severity"] = "INFO"
            tag = "dbus/node/{0}/generic/storage/block/changed".format(
                self.minion_id)
            return res, tag

    @dbus_signal_handler
    def block_add(self, a, d, path):
        res = {}
        res["tags"] = {}
        for e, v in d.iteritems():
            if e.split('.')[-1] == "Block":
                deviceName = ""
                for e in v.get("Device"):
                    deviceName += str(e)
                res["tags"]["DeviceName"] = deviceName[:-1]
                res["tags"]["DeviceNumber"] = str(v.get("DeviceNumber"))
                res["tags"]["Drive"] = str(v.get("Drive")).split(
                    '/')[-1].replace("_", "-")
                res["tags"]["size"] = str(v.get("Size"))
                res["tags"]["ID"] = str(v.get("Id"))
                res["message"] = "New Block Device %s of size %s "\
                                 "GB added" % (res["tags"]["DeviceName"],
                                               str(float(
                                                   res["tags"]["size"]
                                               )/(ONE_GB_IN_KB)))
                res["severity"] = "INFO"
            elif e.split('.')[-1] == "Partition":
                res["tags"]["PartitionNumber"] = str(v.get("Number"))
                res["tags"]["Offset"] = str(v.get("Offset"))
                res["tags"]["size"] = str(v.get("Size"))
                res["tags"]["Table"] = str(v.get("Table")).split('/')[-1]
                res["tags"]["Type"] = str(v.get("Type"))

        if res['tags']:
            tag = "dbus/node/{0}/generic/storage/block/added".format(
                self.minion_id)
            return res, tag

    @dbus_signal_handler
    def block_remove(self, a, d, path):
        for e in d:
            if e.split('.')[-1] == "Block":
                res = {}
                res["tags"] = {}
                res["tags"]["DeviceName"] = str(a.split('/')[-1])
                res["tags"]["Action"] = "Removed"
                res["message"] = "Block Device %s Removed" % (
                    res["tags"]["DeviceName"])
                res["severity"] = "Warning"
                tag = "dbus/node/{0}/generic/storage/block/"\
                      "removed".format(self.minion_id)
                return res, tag

    @dbus_signal_handler
    def mount_state_change(self, a, d, c, path):
        res = {}
        res["tags"] = {}
        if a.split('.')[-1] == "Filesystem":
            mountPoints = []
            for k, v in d.items():
                res["tags"]["DeviceName"] = str(path).split('/')[-1]
                res["tags"]["Action"] = "Device mount state changed"
                for mPoint in v:
                    mountPoint = ""
                    for e in mPoint:
                        mountPoint += str(e)
                    mountPoints.append(mountPoint[:-1])
            res["message"] = "Device %s mounted on following mount points"\
                             ": %s" % (res["tags"]["DeviceName"], ",".join(
                                 mountPoints))
            res["severity"] = "INFO"
            tag = "dbus/node/{0}/generic/storage/mount/changed".format(
                self.minion_id)
            return res, tag

    @dbus_signal_handler
    def network_device_added(self, a, path):
        res = {}
        res["tags"] = {}
        res["tags"]["deviceNo"] = str(a.split('/')[-1])
        res["tags"]["action"] = "added"
        res["message"] = "Network device added"
        res["severity"] = "info"
        tag = "dbus/node/{0}/generic/network/device/added".format(
            self.minion_id)
        return res, tag

    @dbus_signal_handler
    def network_device_removed(self, a, path):
        res = {}
        res["tags"] = {}
        res["tags"]["deviceNo"] = str(a.split('/')[-1])
        res["tags"]["action"] = "removed"
        res["message"] = "Network device removed"
        res["severity"] = "info"
        tag = "dbus/node/{0}/generic/network/device/removed".format(
            self.minion_id)
        return res, tag

    @dbus_signal_handler
    def network_device_changed(self, d, path):
        res = {}
        res["tags"] = {}
        for k, v in d.iteritems():
            if str(k) not in ["StateReason",
                              "ActiveConnection",
                              "AvailableConnections"]:
                res["tags"][str(k)] = str(v)
        if not res["tags"]:
            return None, None
        res["tags"]["deviceNo"] = str(path.split('/')[-1])
        res["message"] = "Network device property changed"
        res["severity"] = "info"
        tag = "dbus/node/{0}/generic/network/device/propertyChanged".format(
            self.minion_id)
        return res, tag

    @dbus_signal_handler
    def glusterd_status(self, a, b, c, path):
        if str(a).split('.')[-1] != "Unit":
            return None, None
        res = {}
        res["tags"] = {}
        res["tags"]["serviceName"] = "Glusterd"
        res["tags"]["ActiveState"] = str(b.get("ActiveState"))
        res["tags"]["SubState"] = str(b.get("SubState"))
        res["message"] = "glusterd process state changed"\
                         " to %s" % (res["tags"]["ActiveState"])
        res["severity"] = "Warning"
        tag = "dbus/node/{0}/glusterfs/service/glusterd".format(self.minion_id)
        return res, tag

    @dbus_signal_handler
    def salt_minion_status(self, a, b, c, path):
        if str(a).split('.')[-1] != "Unit":
            return None, None
        res = {}
        res["tags"] = {}
        res["tags"]["serviceName"] = "salt-minion"
        res["tags"]["ActiveState"] = str(b.get("ActiveState"))
        res["tags"]["SubState"] = str(b.get("SubState"))
        res["message"] = "salt-minion process state changed to %s" % (
            res["tags"]["ActiveState"])
        res["severity"] = "Warning"
        tag = "dbus/node/{0}/generic/service/salt_minion".format(
            self.minion_id)
        return res, tag

    @dbus_signal_handler
    def collectd_status(self, a, b, c, path):
        if str(a).split('.')[-1] != "Unit":
            return None, None
        res = {}
        res["tags"] = {}
        res["tags"]["serviceName"] = "collectd"
        res["tags"]["ActiveState"] = str(b.get("ActiveState"))
        res["tags"]["SubState"] = str(b.get("SubState"))
        res["message"] = "collectd process state changed to %s" % (
            res["tags"]["ActiveState"])
        res["severity"] = "Warning"
        tag = "dbus/node/{0}/generic/service/collectd".format(self.minion_id)
        return res, tag

    @dbus_signal_handler
    def lvm_vg_create(self, a, b, path):
        if b.keys()[0] != "org.storaged.Storaged.VolumeGroup":
            return None, None
        res = {}
        res["tags"] = {}
        res["tags"]['VgName'] = str(b[b.keys()[0]].get('Name'))
        res["tags"]['UUID'] = str(b[b.keys()[0]].get('UUID'))
        res["tags"]['Size'] = str(b[b.keys()[0]].get('Size'))
        res["tags"]['FreeSize'] = str(b[b.keys()[0]].get('FreeSize'))
        tag = "dbus/node/{0}/generic/lvm/vg/create".format(self.minion_id)
        return res, tag

    @dbus_signal_handler
    def lvm_lv_create(self, a, b, path):
        if b.keys()[0] != "org.storaged.Storaged.LogicalVolume":
            return None, None
        res = {}
        res["tags"] = {}
        res["tags"]['LvName'] = str(b[b.keys()[0]].get('Name'))
        res["tags"]['UUID'] = str(b[b.keys()[0]].get('UUID'))
        res["tags"]['Size'] = str(b[b.keys()[0]].get('Size'))
        res["tags"]['Type'] = str(b[b.keys()[0]].get('Type'))
        if res['Type'] != 'pool':
            pass
        else:
            res["tags"]['ThinPool'] = str(b[b.keys()[0]].get(
                'ThinPool')).split('/')
        res["tags"]['VolumeGroup'] = str(b[b.keys()[0]].get(
            'VolumeGroup')).split('/')[-1]
        tag = "dbus/node/{0}/generic/lvm/lv/create".format(self.minion_id)
        return res, tag

    @dbus_signal_handler
    def lvm_lv_delete(self, a, b, path):
        if str(b[0]) != "org.storaged.Storaged.LogicalVolume":
            return None, None
        res = {}
        res["tags"] = {}
        tv = str(a).split('/')
        res["tags"]['LvName'] = tv[-2] + "/" + tv[-1]
        res["tags"]['Action'] = "Removed"
        tag = "dbus/node/{0}/generic/lvm/lv/delete".format(self.minion_id)
        return res, tag

    @dbus_signal_handler
    def lvm_vg_delete(self, a, b, path):
        if str(b[0]) != "org.storaged.Storaged.VolumeGroup":
            return None, None
        res = {}
        res["tags"] = {}
        tv = str(a).split('/')
        res["tags"]['VgName'] = tv[-1]
        res["tags"]['Action'] = "Removed"
        tag = "dbus/node/{0}/generic/lvm/vg/delete".format(self.minion_id)
        return res, tag


def get_enabled_methods(cb):
    """
    This function reads the configuration file skynetd.conf and
    return's a dictionary with function name as key and function as
    value of all the enabled methods
    """
    try:
        with open(SKYNET_CONF_FILE, 'r') as f:
            conf = json.loads(f.read())
    except IOError:
        logger.error(
            "Configuration file: /etc/skynet/skynet.conf could not be read")
        exit(1)

    enabled_methods = []
    for group, info in conf.iteritems():
        if not conf[group]['enabled']:
            continue
        for method, enabled in conf[group]["methods"].iteritems():
            if enabled:
                enabled_methods.append(str(method))
    all_methods = inspect.getmembers(cb)
    em = {}
    for el in all_methods:
        if el[0] in enabled_methods:
            em.update({el[0]: el[1]})
    return em
