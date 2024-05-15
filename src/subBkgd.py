#!/usr/bin/env python3
from readGPC import *
from matplotlib.widgets import Button, RadioButtons
from scipy.interpolate import interp1d, CubicSpline, Akima1DInterpolator

def bkground_y(x, zero_points): # fit linear or spline background given `zero_points` and return a `y` list given `x`
    zero_points_t = np.array(zero_points).T
    zero_points_t = zero_points_t[:, zero_points_t[0].argsort()] # make sure x is in increasing order
    if bg_type == 'Akima':
        f = Akima1DInterpolator(*zero_points_t)
        f.extrapolate = True # extend to outside range
    elif bg_type == 'Spline':
        f = CubicSpline(*zero_points_t, extrapolate=True)
    elif bg_type == 'Linear':
        f = interp1d(*zero_points_t, fill_value="extrapolate")
    else:
        raise ValueError("Unknown fitting method")
    return f(x)

def closestXY_index(dataX, valX, dataY, valY): # find the closest value to `val` in `data`
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    diff = ((dataX-valX)/(x1-x0))**2+((dataY-valY)/(y1-y0))**2 # calculate distance, but need to be normalized according to current plot range
    return np.argmin(diff)

def mouse_event(event):
    global bg_list, bg_line
    if not (event.dblclick and event.inaxes is ax): # only respond to double clicks within plot canvas
        return
    if bg_line: # remove previous background if existent
        bg_line.remove()
        bg_list = bg_line = None
    i = closestXY_index(x, event.xdata, y, event.ydata)
    zero_point = (x[i], y[i])
    zp_list.append(zero_point)
    pt_list.append(ax.scatter(*zero_point, c='r', s=80, alpha=0.4, zorder=999))
    plt.draw() # update

def bClPr_onclick(event): # clear previous point
    global bg_list, bg_line
    if not zp_list:
        print("No previous point to clear.                                                             \a", end='\r')
        return
    zp_list.pop()
    pt_list.pop().remove()
    if bg_line: # remove previous background if existent
        bg_line.remove()
        bg_list = bg_line = None
    plt.draw() # update

def bClAl_onclick(event): # clear all points
    global bg_list, bg_line
    if not zp_list:
        print("No points to clear.                                                                     \a", end='\r')
        return
    for i in pt_list:
        i.remove()
    if bg_line:
        bg_line.remove()
        bg_list = bg_line = None
    del zp_list[:]
    del pt_list[:]
    plt.draw() # update

def bFit_onclick(event): # fit background
    global bg_list, bg_line
    if len(zp_list) < 2:
        print("At least two points need to be selected before a background curve can be fit.           \a", end='\r')
        return
    if bg_line: # remove previous background if existent
        bg_line.remove()
    bg_list = bkground_y(x, zp_list)
    bg_line = ax.plot(x, bg_list, '--', label='bkgd')[0]
    ax.legend()
    plt.draw() # update
    print("A background curve has been fit and shown. Click 'SubBkgd' to continue...               \a", end='\r')

def bSub_onclick(event): # subtract background
    global bg_list, bg_line, y_new
    if not bg_line:
        print("Please fit a background curve first.                                                    \a", end='\r')
        return
    y_new = y - bg_list
    _, y_new, ymin, ymax = normalize(x, y_new)

    plt.figure(2, figsize=FIG_SIZE, dpi=FIG_DPI_DISPLAY)
    plt.plot(x, y_new, label='bkgd subtracted')
    plt.xlim(NORM_RANGE)
    plt.ylim(ymin-MARGIN, ymax+MARGIN)
    plt.xlabel(XLABEL)
    plt.ylabel(YLABEL)
    plt.tight_layout()
    plt.legend()
    plt.close(1)

def rbType_onclick(event):
    global bg_type
    bg_type = event

zp_list = [] # zero points (x, y)
pt_list = [] # plt.scatter objects
bg_list = None # background (x, y)
bg_line = None # plt.plot Line2D object
bg_type = BKGROUND_TYPE
y_new = None

argv, dir_o, baseline = getInput()
res = readFile(argv[0], baseline)
if res is None:
    sys.exit()
x, y, ymin, ymax = res

fig = plt.figure(1)
ax = plt.gca()
fig.canvas.mpl_connect('button_press_event', mouse_event)

plt.plot(x, y, label='raw')
plt.xlim(NORM_RANGE)
plt.ylim(ymin-MARGIN, ymax+MARGIN)
plt.xlabel(XLABEL)
plt.ylabel(YLABEL)
plt.subplots_adjust(0.12, 0.1, 0.97, 0.83)
plt.legend(fontsize=LEGEND_FONTSIZE*5//4)

bClPr = Button(plt.axes((0.05, 0.8875, 0.15, 0.05)), 'ClearPrev')
bClPr.on_clicked(bClPr_onclick)
bClAl = Button(plt.axes((0.25, 0.8875, 0.15, 0.05)), 'ClearAll')
bClAl.on_clicked(bClAl_onclick)
bFit = Button(plt.axes((0.45, 0.8875, 0.15, 0.05)), 'FitBkgd')
bFit.on_clicked(bFit_onclick)
bSub = Button(plt.axes((0.65, 0.8875, 0.15, 0.05)), 'SubBkgd')
bSub.on_clicked(bSub_onclick)
rbType = RadioButtons(plt.axes((0.85, 0.85, 0.10, 0.125)), ('Akima', 'Spline', 'Linear'))
if BKGROUND_TYPE == 'Spline':
    rbType.set_active(1)
elif BKGROUND_TYPE == 'Linear':
    rbType.set_active(2)
rbType.on_clicked(rbType_onclick)

print("\nDouble click on curve points that need to be zeroed. Then click 'FitBkgd' to continue...", end='\r')
plt.show()

if y_new is None:
    if os.name == 'nt': atexit.unregister(os.system) # on Windows, no need to pause anymore
    print("Cancelled by user.                                                                      ")
    sys.exit()

print("The background-subtracted trace is shown in a new window. Close the window to continue...\a", end='\r')
plt.show()

fname = p.splitext(argv[0])[0]
data = np.array((x, y_new))

types = BKGROUND_SAVE
if types in (0, 1, 2, 3):
    print("                                                                                         ", end='\r') # clear line
else: # ask if is not accepted value
    print("What file would you like to save the new trace as? The file will be compatible with `readGPC`.\n- 0 : None\n- 1 : CSV spreadsheet\n- 2 : NPY binary\n- 3 : Both")
    types = {'0': 0, '1': 1, '2': 2, '3': 3}.get(input("Please enter a single digit number as instructed above: "), 0) # map input str to 0 (default) to 3

if types & 1:
    fname2 = fname+'_bkgd.csv'
    with open(fname2, 'w', newline='') as f:
        w = csv.writer(f, delimiter=DELIMITER)
        w.writerow((HEADER_X, HEADER_Y)) # header
        w.writerows(data.T)
    print('Saved to '+fname2)
if types & 2:
    fname2 = fname+'_bkgd.npy'
    np.save(fname2, data)
    print('Saved to '+fname2)
