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

from twisted.internet import reactor, task
from twisted.internet.serialport import SerialPort
from twisted.python import usage

from datafiles import FODatafile

class THOptions(usage.Options):
    optParameters = [
        ['baudrate', 'b', 115200, 'Serial baudrate'],
        ['port', 'p', '/dev/tty.usbserial-A700ejg7', 'Serial port to use'],
        ['filename', 'f', 'datafile.txt', 'datafile to append to'],
        ['watch_url', 'u', None, 'URL for watch information'],
        ['data_dir', 'd', 'data', 'Datafile directory to write to'],
        ['sample_delay', 's', '5.0', 'Seconds between samples'],
        ['junktime', 'j', 2, 'Seconds worth of data to discard at start'],
        ['runtime', 'r', 0, 'Seconds to capture data'],
        ]

class FlexOpt(LineReceiver):
    def __init__(self, filename, data_dir=None, run_time=0, junk_time=2):
        self.dfile = FODatafile(filename, data_dir)
        logging.debug('Filename: %s Initial delay time: %f' % (self.dfile.filename, junk_time))
        if run_time > 0:
            logging.debug('Run time: %d seconds' % run_time)
        self.go_time = time.time() + junk_time
        self.end_time = self.go_time + run_time
        self.run_time = run_time

    def connectionMade(self):
        logging.debug('Connection made to the flexOptometer!')
        self.tzero = time.time()

    def do_sample(self):
        """
        Do a single sample on demand. Triggers lineReceived.
        """
        self.transport.write('\rrea\r')

    def lineReceived(self, line):
        if time.time() < self.go_time:
            return

        ts = time.time() - self.tzero
        str = line.strip()

        if len(str) == 0:
            return

        if str[0] == '*':
            logging.warn('Ignoring line "%s"' % str)
            return

        if str == 'Ok':
            return

        if str == 'ERROR-Command not recognized.':
            logging.error('Unknown command!')
            return

        try:
            fv = float(str)
        except ValueError, ve:
            logging.exception('Error parsing as float: ')
            return

        if fv < 0.0:
            logging.warn('Dropping negative value %f' % fv)
            return

        logstr = '%s\t%s\n' % (ts, fv)
        logging.debug(logstr.strip())

        self.dfile.write_datum(ts, fv)

        if self.run_time > 0:
            if time.time() > self.end_time:
                logging.info('Done.')
                self.dfile.close()
                self.transport.write('\r')
                self.transport.write('bee\r')
                self.transport.loseConnection()
                reactor.stop()

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

    baudrate = int(o.opts['baudrate'])
    port = o.opts['port']
    filename = o.opts['filename']
    data_dir = o.opts['data_dir']
    junk_time = int(o.opts['junktime'])
    run_time = int(o.opts['runtime'])
    sample_delay = float(o.opts['sample_delay'])
    watch_url = o.opts['watch_url']

    logging.debug('About to open port %s' % port)
    fo = FlexOpt(filename, data_dir=data_dir, run_time=run_time,
                 junk_time=junk_time, watch_url=watch_url)
    s = SerialPort(fo, port, reactor, baudrate=baudrate)

    # Setup periodic sampling call
    pt = task.LoopingCall(fo.do_sample)
    # Setup interval for same
    pt.start(sample_delay)

    reactor.run()
