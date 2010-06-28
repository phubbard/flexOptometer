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
    def __init__(self, filename, data_dir=None):
        if data_dir:
            self.filename = data_dir + os.pathsep + filename
        else:
            self.filename = filename

        self.fh = open(self.filename, 'w')
        self.write_fileheader()

    def close(self):
        self.fh.close()

    def write(self, data):
        self.fh.write(data)

    def write_datum(self, time, reading):
        self.fh.write('%f\t%f' % (time, reading))
        self.fh.write(os.linesep)

    def write_fileheader(self):
        buf = []
        rn = datetime.date.today()

        buf.append('Filename: %s' % self.filename)
        buf.append('Copyright Paul Hubbard (phubbard@watchotaku.com) %d' % rn.year)
        buf.append('See http://github.com/phubbard/flexOptometer')
        buf.append('Timestamp: %s' % datetime.datetime.now())
        buf.append('UTC timestamp: %s' % datetime.datetime.utcnow())
        buf.append('Time(seconds)\tLux')

        for line in buf:
            self.fh.write(line)
            self.fh.write(os.linesep)
