#!/usr/bin/env python3
from readGPC import *
from matplotlib.widgets import Button
LEGEND = ('start', 'dividing', 'end', 'trace', 'polymer', 'monomer', 'bkgd')

def closestX_index(dataX, valX): # find the closest value to `val` in `data`
    return np.argmin(np.abs(dataX-valX))

def mouse_event(event):
    if not (event.dblclick and event.inaxes is ax): # only respond to double clicks within plot canvas
        return
    l = len(ind_list)
    if l >= 3: # proceed to calc
        bFit_onclick(None)
        return
    i = closestX_index(x, event.xdata)
    if l and i <= ind_list[-1]:
        print("The current selected elution time must be greater than the previous one.                \a", end='\r')
        return
    ind_list.append(i)
    pt_list.append(ax.scatter(x[i], y[i], c='C'+str(l+1), s=80, alpha=0.4, zorder=999, label=LEGEND[l]))
    if l == 2: # end point
        rg_list.append(ax.fill_between(x[ind_list[1]:i+1], y[ind_list[1]:i+1], color='0.6', alpha=0.4, label=LEGEND[5]))
        ax.legend(*([ll[j] for j in (0, 1, 2, 4, 3, 5)] for ll in ax.get_legend_handles_labels())) # switch order
        plt.draw()
        return
    elif l == 1: # dividing point
        rg_list.append(ax.fill_between(x[ind_list[0]:i+1], y[ind_list[0]:i+1], color='C0', alpha=0.4, label=LEGEND[4]))
    ax.legend()
    plt.draw() # update

def bClPr_onclick(event): # clear previous point
    l = len(ind_list)
    if not l:
        print("No previous point to clear.                                                             \a", end='\r')
        return
    ind_list.pop()
    pt_list.pop().remove()
    if l > 1:
        rg_list.pop().remove()
    if bkgd_line:
        del bkgd_list[:]
        bkgd_line.pop().remove()
        if l > 2: # redraw region because baseline is reverted
            rg_list[0].remove()
            rg_list[0] = ax.fill_between(x[ind_list[0]:ind_list[1]+1], y[ind_list[0]:ind_list[1]+1], color='C0', alpha=0.4, label=LEGEND[4])
    ax.legend()
    plt.draw() # update

def bClAl_onclick(event): # clear all points
    if not ind_list:
        print("No points to clear.                                                                     \a", end='\r')
        return
    for i in pt_list:
        i.remove()
    for i in rg_list:
        i.remove()
    del ind_list[:]
    del pt_list[:]
    del rg_list[:]
    if bkgd_line:
        del bkgd_list[:]
        bkgd_line.pop().remove()
    ax.legend()
    plt.draw() # update

def bSub_onclick(event): # subtract/undo a linear baseline defined by the first and last points
    if len(ind_list) < 3:
        print("This function will only work after all the start / dividing / end points are selected.  \a", end='\r')
        return
    if bkgd_line:
        del bkgd_list[:]
        bkgd_line.pop().remove()
        rg_list[0].remove(); rg_list[1].remove()
        rg_list[0] = ax.fill_between(x[ind_list[0]:ind_list[1]+1], y[ind_list[0]:ind_list[1]+1], color='C0', alpha=0.4, label=LEGEND[4])
        rg_list[1] = ax.fill_between(x[ind_list[1]:ind_list[2]+1], y[ind_list[1]:ind_list[2]+1], color='0.6', alpha=0.4, label=LEGEND[5])
        ax.legend()
        plt.draw()
        print("Background subtraction has been reverted.                                               \a", end='\r')
        return

    x1, x2, y1, y2 = x[ind_list[0]], x[ind_list[2]], y[ind_list[0]], y[ind_list[2]]
    bkgd_line.append(ax.plot((x1, x2), (y1, y2), '-.', c='C0', label=LEGEND[6])[0])
    for i in range(ind_list[0], ind_list[2]+1):
        bkgd_list.append((y2-y1)/(x2-x1)*(x[i]-x1)+y1)
    rg_list[0].remove(); rg_list[1].remove() # need to redraw regions after baseline subtraction
    rg_list[0] = ax.fill_between(x[ind_list[0]:ind_list[1]+1], y[ind_list[0]:ind_list[1]+1], bkgd_list[:ind_list[1]-ind_list[0]+1], color='C0', alpha=0.4, label=LEGEND[4])
    rg_list[1] = ax.fill_between(x[ind_list[1]:ind_list[2]+1], y[ind_list[1]:ind_list[2]+1], bkgd_list[ind_list[1]-ind_list[0]:], color='0.6', alpha=0.4, label=LEGEND[5])
    ax.legend()
    print("Background subtraction has been applied.                                                \a", end='\r')
    plt.draw() # update

def bFit_onclick(event):
    if len(ind_list) < 3:
        print("This function will only work after all the start / dividing / end points are selected.  \a", end='\r')
        return
    a1 = a2 = 0
    for i in range(ind_list[0], ind_list[1]): # subtract linear baseline
        yv = y[i]
        if bkgd_list:
            yv -= bkgd_list[i-ind_list[0]]
        a1 += (x[i+1]-x[i])*yv
    for i in range(ind_list[1], ind_list[2]): # same as above
        yv = y[i]
        if bkgd_list:
            yv -= bkgd_list[i-ind_list[0]]
        a2 += (x[i+1]-x[i])*yv
    print("                                                                                         \a", end='\r') # clear line
    print("Polymer : Monomer =", a1, ":", a2)
    print("Conversion =", a1/(a1+a2))
    plt.close()
    sys.exit()

bkgd_line = [] # plt.plot object
bkgd_list = [] # linear background (x,y) within range
ind_list = [] # index list for start/dividing/end points
pt_list = [] # plt.scatter objects
rg_list = [] # plt.fill_between objects

argv, dir_o, baseline = getInput()
res = readFile(argv[0], baseline)
if res is None:
    sys.exit()
x, y, ymin, ymax = res

fig = plt.figure()
ax = plt.gca()
fig.canvas.mpl_connect('button_press_event', mouse_event)

plt.rcParams['legend.fontsize'] = LEGEND_FONTSIZE*5//4
plt.plot(x, y, label=LEGEND[3])
plt.xlim(NORM_RANGE)
plt.ylim(ymin-MARGIN, ymax+MARGIN)
plt.xlabel(XLABEL)
plt.ylabel(YLABEL)
plt.subplots_adjust(0.12, 0.1, 0.97, 0.85)
plt.legend()

bClPr = Button(plt.axes((0.04, 0.9, 0.2, 0.05)), 'ClearPrev')
bClPr.on_clicked(bClPr_onclick)
bClAl = Button(plt.axes((0.28, 0.9, 0.2, 0.05)), 'ClearAll')
bClAl.on_clicked(bClAl_onclick)
bSub = Button(plt.axes((0.52, 0.9, 0.2, 0.05)), 'SubBkgd')
bSub.on_clicked(bSub_onclick)
bFit = Button(plt.axes((0.76, 0.9, 0.2, 0.05)), 'CalcConv')
bFit.on_clicked(bFit_onclick)

print("\nDouble click on the starting and ending elution times for the polymer and monomer peaks.", end='\r')
plt.show()

if len(ind_list) >= 3: # proceed to calc
    bFit_onclick(None)
if os.name == 'nt': atexit.unregister(os.system) # on Windows, no need to pause anymore
print("Cancelled by user.                                                                      ")
