#!/usr/bin/env python3
import os
if os.name == 'nt':
    import atexit
    atexit.register(os.system, 'pause') # on Windows, always pause before exiting

import csv
import numpy as np
import matplotlib.pyplot as plt
import os.path as p
import sys
import time
import logging

sys.dont_write_bytecode = True # do not produce garbage cache (because the config py files to import are subject to constant changes)
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

#dir_t = p.dirname(p.realpath(__file__))
#f = open(p.join(dir_t, 'config.py')); exec(f.read()); f.close()
#f = open(p.join(dir_t, 'configGPC.py')); exec(f.read()); f.close()
# two ways of loading config py files: above (commented out): execfile; below (used here): import (need to add app folder to import PATH; see __init__.py)
from config import *
from configGPC import *
plt.rcParams.update(PLT_RCPARAMS)
num = 0 # index of GPC trace

def normalize(xVals, yVals):
    iBegin = np.searchsorted(xVals, NORM_RANGE[0])
    iEnd = np.searchsorted(xVals, NORM_RANGE[1])
    # mask = np.bitwise_and(xVals > NORMRANGE[0], xVals < NORMRANGE[1])
    yValsR = yVals[iBegin:iEnd]
    yMin = np.min(yValsR)
    yMax = np.max(yValsR)
    yVals2 = (yVals-yMin)/(yMax-yMin) # normalize to [0, 1]
    if AUTO_BASELINE:
        xBegin = xVals[iBegin]
        xEnd = xVals[iEnd-1]
        yBegin = yVals2[iBegin]
        yEnd = yVals2[iEnd-1]
        slope = (yBegin-yEnd)/(xBegin-xEnd)
        yVals2 -= slope*(xVals-xBegin)+yBegin # subtract a linear baseline according to NORMRANGE
        yValsR = yVals2[iBegin:iEnd]
        yMin2 = -np.min(yValsR) # in case of negative peak
        yMax2 = np.max(yValsR)
        if ALLOW_NEG_NORM and yMax2 < yMin2: # predominant negative peak
            norm = yMin2
        else: # predominant negative peak
            norm = yMax2
        yVals2 /= norm
        yMin2 /= norm
        yMax2 /= norm
    else: # predominant negative peak detection methods are different: AUTOBASELINE==True: after subtracting the linear background, see whether the positive or negative maximum magnitude is larger; AUTOBASELINE==False: see whether the average y value is greater or less than 1/2  
        if ALLOW_NEG_NORM and np.mean(yVals2[iBegin:iEnd]) < 0.5: # predominant negative peak
            yVals2 -= 1
            yMin2 = 1; yMax2 = 0
        else:
            yMin2 = 0; yMax2 = 1
    return (xVals, yVals2, -yMin2, yMax2) # the last two will be useful when determining the y-range of the plot

def readCSV(f): # f: File Object
    data = []
    r = csv.reader(f, skipinitialspace=True, delimiter=DELIMITER)
    dataStart = False
    for row in r:
        if not row: continue # empty row
        if dataStart:
            try: # see if it is indeed numerical data
                data.append((float(row[xIndex]), float(row[yIndex])))
            except: pass
        else:
            try: # find corresponding column indices
                xIndex = row.index(HEADER_X)
                yIndex = row.index(HEADER_Y)
                dataStart = True
            except: pass
    return np.array(data, dtype=float).T # transpose

def readClipBoard():
    import win32clipboard
    from io import StringIO
    win32clipboard.OpenClipboard()
    data = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()
    return readCSV(StringIO(data, newline=''))

def readData(filename): # input can be either csv or npy; output is sorted raw (x, y) array
    try:
        xVals, yVals = np.load(filename)
        print('[NPY file]')
    except:
        try:
            with open(filename, newline='') as f:
                xVals, yVals = readCSV(f)
            print('[CSV file]')
        except:
            print('is not a valid CSV or NPY file.\r! ')
            return None
    sortedID = np.argsort(xVals)
    return xVals[sortedID], yVals[sortedID] # make sure X values are in ascending order

def readFile(filename, baseline=None): # `filename` can also be: '{CliboardData}'
    print(num+1, ':', filename, end=' ')
    if filename == '{CliboardData}':
        try:
            xVals, yVals = readClipBoard()
            print('[CSV format]')
        except:
            print('is not of valid CSV format.\r! ')
            return None
    else:
        res = readData(filename)
        if res is None: return None # fail
        xVals, yVals = res
    if baseline is not None: # subtract baseline
        yBase = np.interp(xVals, *baseline) # baseline data might contain different retention times, in which case interpolation is necessary
        yVals -= yBase*BASELINE_PARAMS[2]
    return normalize(xVals, yVals)

def plotFile(filename, offset=0):
    global num, ymin, ymax
    data = readFile(filename, baseline)
    if data is None:
        return
    num += 1
    x, y, _ymin, _ymax = data
    longName = p.splitext(p.basename(filename))[0]
    output[0].append(longName)
    output[1].append(x)
    output[1].append(y)
    y += offset
    _ymin += offset
    _ymax += offset
    if _ymin < ymin:
        ymin = _ymin
    if _ymax > ymax:
        ymax = _ymax
    plt.plot(x, y, LINE_MARKER, label=longName.replace(FILENAME_ESCAPE_CHAR, '\\') if LONG_NAME else str(num))

def getInput():
    argv = sys.argv[1:] # disregard argv[0] (self)
    try:
        dir_o = p.dirname(argv[0]) # the dir of the first input file
    except:
        if os.name != 'nt': # reading clipboard data is only supported on Windows
            print('Empty or invalid input [Note: Clipboard data reading is not supported on this OS].')
            sys.exit()
        print('Warning: Empty or invalid input. Will try reading data from clipboard.')
        dir_o = '.'
        argv = ('{CliboardData}',)
    if not BASELINE_PARAMS[2]: # baseline function not turned on
        return argv, dir_o, None # no baseline
    if BASELINE_PARAMS[0]: # always apply baseline
        filename = p.join(p.dirname(p.realpath(__file__)), BASELINE_PARAMS[1])
        print('0 :', filename, end=' (baseline) ')
        baseline = readData(filename)
    else: # check if baseline file is provided
        baseline = None
        for i, fname in enumerate(argv):
            if p.splitext(p.basename(fname))[0] != BASELINE_PARAMS[1]: continue # must match base name
            print('0 :', fname, end=' (baseline) ')
            baseline = readData(fname)
            if baseline is not None:
                del argv[i]
                break
    if baseline is not None:
        if (not BASELINE_ASK) or input("Apply this baseline to all traces? [y/n] ").lower() == 'y':
            print('Baseline ( #0, *', BASELINE_PARAMS[2], ') will be applied to all traces.')
        else:
            print("Baseline will not be applied.")
            baseline = None
    return argv, dir_o, baseline

if __name__ == "__main__":
    argv, dir_o, baseline = getInput()

    fn = SAVE_FILENAME
    if '|' in fn: # format file name for saving
        fnl = fn.split('|')
        for i, x in enumerate(fnl):
            if x[:9] == 'datetime:':
                fnl[i] = time.strftime(x[9:], time.localtime())
            if x == 'gpcname':
                fnl[i] = GPC_NAME
        fn = ''.join(fnl)
        if fnl[0] == 'dir':
            fn = p.join(dir_o, fn[3:])

    ymin = 0; ymax = 0 # take into account negative peaks, then the plot range will be [ymin, ymax] instead of [0, 1]
    output = [[], []]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=FIG_DPI_DISPLAY)
    fig.patch.set_visible(False)
    ax.patch.set_visible(False) # transparent background

    for i, fname in enumerate(argv):
        plotFile(fname, offset=i*OFFSET)
    if not num:
        print('No valid input file to plot.')
        sys.exit()
    plt.legend()
    plt.xlabel(XLABEL)
    plt.ylabel(YLABEL)
    if AUTO_CROP:
        plt.xlim(NORM_RANGE)
        plt.ylim(ymin-MARGIN, ymax+MARGIN)
    plt.tight_layout()
    plt.show()

    print()
    types = SAVE_TYPES.lower()
    if types == 'ask':
        print("Which of the following file type(s) would you like to save as:\n- PNG : overlaid bitmap graphic\n- SVG : overlad vector graphic\n- CSV : combined spreadsheet of normalized traces\n- NPY : separate NumPy binary files of normalized traces")
        types = input('Please enter here; can be none, one, or several file types. In the last case, separate them with spaces. Use the 3-letter phrases defined above (case-insensitive): ').lower()
    types = types.split()

    if not types:
        if os.name == 'nt': atexit.unregister(os.system) # on Windows, no need to pause anymore
        sys.exit()
    if 'png' in types:
        fname = fn+'.png'
        fig.savefig(fname, transparent=True, dpi=FIG_DPI_SAVE)
        print('Saved to '+fname)
    if 'svg' in types:
        fname = fn+'.svg'
        fig.savefig(fname)
        print('Saved to '+fname)
    if 'csv' in types:
        from itertools import zip_longest
        rows = zip_longest(*output[1], fillvalue='') # in case array lengths are different, need to fill empty strings
        fname = fn+'.csv'
        with open(fname, 'w', newline='') as f:
            f.write(',,'.join(output[0]))
            f.write('\n')
            csv.writer(f).writerows(rows)
        print('Saved to '+fname)
    if 'npy' in types:
        for i, fname in enumerate(output[0]):
            fname += '.npy'
            if p.isfile(fname) and input("Warning: File '" + fname + "' will be overwritten! Continue? [y/n] ").lower() != 'y':
                print("This file will not be saved.")
                continue
            np.save(fname, np.array(output[1][2*i:2*i+2]))
            print('- Saved to '+fname)
