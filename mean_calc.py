#!/usr/bin/env python
"""
@file mean_calc.py
@author paul hubbard
@date 6/9/10
@brief calculate mean value - used for an average background to subtract.
"""

import logging
import math
import sys

from twisted.python import usage

class MCOptions(usage.Options):
    optParameters = [
        ['filename', 'f', 'background.txt', 'Filename to process'],
    ]

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, \
                format='%(asctime)s %(levelname)s [%(funcName)s] %(message)s')

    o = MCOptions()
    try:
        o.parseOptions()
    except usage.UsageError, errortext:
        logging.error('%s %s' % (sys.argv[0], errortext))
        logging.info('Try %s --help for usage details' % sys.argv[0])
        raise SystemExit, 1

    filename = o.opts['filename']

    logging.debug('filename: ' + filename)

    fh = open(filename)

    sum = 0.0
    max = 0.0
    min = 9999999999.0

    num_pts = 0

    for line in fh:
        ts, value = line.split('\t')
        val = float(value)
        sum = sum + val

        if val < min:
            min = val
        if val > max:
            max = val

        logging.debug('val: %s as f: %e' % (value.strip(), float(value)))
        num_pts = num_pts + 1

    if num_pts == 0:
        logging.warn('No data found!')
        sys.exit(1)

    mean = sum / num_pts
    logging.info('%d points, sum %e, mean %e, min %e, max %e' %
                 (num_pts, sum, mean, min, max))
