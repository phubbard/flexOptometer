#!/usr/bin/env python

"""
@file datafiles.py
@author Paul Hubbard
@brief Data file routines for flexOptometer
"""
import os
import datetime

class FODatafile():
    """
    Wrapper class for datafiles. Idea is to encapsulate headers and such,
    with an eye out for later changing save formats.
    """
    def __init__(self, filename, data_dir=None, watch_url=None, focal_length=None):
        if data_dir:
            self.filename = data_dir + '/' + filename
        else:
            self.filename = filename

        self.watch_url = watch_url
        self.focal_length = focal_length

        self.fh = open(self.filename, 'w')
        self.write_fileheader()

    def close(self):
        return self.fh.close()

    def flush(self):
        return self.fh.flush()

    def write_datum(self, time, reading):
        self.fh.write('%f\t%f' % (time, reading))
        self.fh.write(os.linesep)

    def write_fileheader(self):
        buf = []
        rn = datetime.date.today()

        buf.append('Filename: %s' % self.filename)
        if self.watch_url:
            buf.append('Watch info at: ' + self.watch_url)
        if self.focal_length:
            buf.append('Focal length: %f cm' % self.focal_length)
        buf.append('Copyright Paul Hubbard (phubbard@watchotaku.com) %d' % rn.year)
        buf.append('License: http://creativecommons.org/licenses/by/3.0/us/')
        buf.append('See http://watchotaku.com/display/swr/Measure+luminosity')
        buf.append('Timestamp: %s' % datetime.datetime.now())
        buf.append('UTC timestamp: %s' % datetime.datetime.utcnow())
        buf.append('')
        buf.append('Time(seconds)\tLux')

        for line in buf:
            self.fh.write(line)
            self.fh.write(os.linesep)
