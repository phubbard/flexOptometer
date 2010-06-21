#!/usr/bin/env python

"""
@file flexOptometer/main.py
@author Paul Hubbard
@date 6/6/10
@brief Automate DAQ with a flexOptometer over usb or serial
"""

import sys
import time
import logging

from twisted.protocols.basic import LineReceiver

from twisted.internet import reactor
from twisted.internet.serialport import SerialPort
from twisted.python import usage

class THOptions(usage.Options):
    optParameters = [
        ['baudrate', 'b', 115200, 'Serial baudrate'],
        ['port', 'p', '/dev/tty.usbserial-A700ejg7', 'Serial port to use'],
        ['filename', 'f', 'datafile.txt', 'datafile to append to'],
        ['junktime', 'j', 2, 'Seconds worth of data to discard at start'],
        ['runtime', 'r', 0, 'Seconds to capture data'],
        ]

class FlexOpt(LineReceiver):
    def __init__(self, filename,  run_time=0, junk_time=2):
        self.fh = open(filename, 'w+')
        logging.debug('Filename: %s Delay time: %f' % (filename, junk_time))
        if run_time > 0:
            logging.debug('Run time: %d seconds' % run_time)
        self.go_time = time.time() + junk_time
        self.end_time = self.go_time + run_time
        self.run_time = run_time

    def connectionMade(self):
        logging.debug('Connection made!')
        # set continuous sampling mode
        self.transport.write('\rreac\r')
        self.tzero = time.time()

    def lineReceived(self, line):
        if time.time() < self.go_time:
            return

        ts = time.time() - self.tzero
        str = line.strip()
        if str[0] == '*':
            logging.warn('Ignoring line "%s"' % str)
            return

        fv = float(str)
        if fv < 0.0:
            logging.warn('Dropping negative value %f' % fv)
            return

        logstr = '%s\t%s\n' % (ts, str)
        logging.debug(logstr.strip())

        self.fh.write(logstr)

        if self.run_time > 0:
            if time.time() > self.end_time:
                logging.info('Done.')
                self.fh.close()
                self.transport.write('\r')
                self.transport.write('beep\r')
                self.transport.loseConnection()
                reactor.stop()
                return


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, \
                format='%(asctime)s %(levelname)s [%(funcName)s] %(message)s')

    o = THOptions()
    try:
        o.parseOptions()
    except usage.UsageError, errortext:
        logging.error('%s %s' % (sys.argv[0], errortext))
        logging.info('Try %s --help for usage details' % sys.argv[0])
        raise SystemExit, 1

    if o.opts['baudrate']:
        baudrate = int(o.opts['baudrate'])

    port = o.opts['port']
    filename = o.opts['filename']
    junk_time = int(o.opts['junktime'])
    run_time = int(o.opts['runtime'])

    logging.debug('About to open port %s' % port)
    s = SerialPort(FlexOpt(filename, run_time=run_time, junk_time=junk_time),
                   port, reactor, baudrate=baudrate)
    reactor.run()
