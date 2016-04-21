#!/usr/bin/env python
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

import signal
import threading
import os
import dbus
import glib
from dbus.mainloop.glib import DBusGMainLoop
import callback
import salt.client
from logger import logger, handler

RUN = True
current_methods = {}


def mainSource(loop):
    loop.run()


def update_listener(cb, bus):
    global current_methods
    enabled_methods = callback.get_enabled_methods(cb)
    poplist = []
    # unregister the signals that are not in the latest config file
    for key, value in current_methods.iteritems():
        if key not in enabled_methods:
            logger.debug("Unregistering the signal: %s", key)
            value.remove()
            poplist.append(key)
    for el in poplist:
        current_methods.pop(el)

    # register the signals that are newly added in the latest config file
    for key, value in enabled_methods.iteritems():
        if key not in current_methods:
            logger.debug("Registering the signal: %s", key)
            signalMatch = bus.add_signal_receiver(
                value,
                signal_name=callback.cb_info[key]['signal_name'],
                dbus_interface=callback.cb_info[key]['dbus_interface'],
                bus_name=callback.cb_info[key]['bus_name'],
                path=callback.cb_info[key]['path'],
                path_keyword='path'
            )
            current_methods.update({key: signalMatch})


def signalHandler(loop, cb, bus):
    """
    signal handler to handle sighup and sigterm signals
    """
    def sighup_handler(signal, frame):
        logger.info("Reloading skynetd")
        update_listener(cb, bus)

    def sigterm_handler(signal, frame):
        logger.info("Terminating skynetd")
        loop.quit()
        global RUN
        RUN = False

    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGHUP, sighup_handler)
    signal.pause()


class Skynetd():

    def run(self):
        logger.info("Initializing skynetd")
        # Using Dbus-python's default mainloop to listen to the events
        DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()

        # creating a salt caller object, this is used to push events using
        # salt's eventing framework
        caller = salt.client.Caller()

        cb = callback.Callback(caller)

        # this initializes/updates the interested signals
        # (read from config file) to be listened by the bus
        update_listener(cb, bus)

        loop = glib.MainLoop()
        glib.threads_init()

        # create a thread to run the main loop which will listen to the dbus
        # and push the events to salt-master
        t = threading.Thread(target=mainSource, args=(loop,))
        t.start()

        # this will continue and listen to external signals (sighup,sigterm)
        # if sighup, the signals to be listened is reread from the config file
        # if sigterm, the daemon will be terminated
        logger.info("Started skynetd to listen for external signals")

        while RUN:
            signalHandler(loop, cb, bus)
        logger.info("Terminated skynetd")


def main():
    try:
        Skynetd().run()
        exit(0)
    except Exception as e:
        logger.error("Skynet Initialization failed: %s", str(e))
        pass


if __name__ == "__main__":
    main()
