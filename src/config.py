# settings (for GPC-specific ones, see configGPC.py)

OFFSET = 0. # distance b/w curves along y
MARGIN = 0.1 # vertical margin space of the plot
AUTO_BASELINE = True # subtract a linear baseline according to the starting and ending points defined in NORMRANGE
AUTO_CROP = True # adjust plot range according to NORMRANGE
LONG_NAME = True # show filename or index in legend
FILENAME_ESCAPE_CHAR = '!' # this character in the filename will be escaped into '\' (you can therefore type LaTeX formula in the filename, e.g., $!bf{S!alpha_{2k}}$.csv, where !bf{} means bold font and !alpha for greek letter alpha)
XLABEL = 'Retention Time (min)'
YLABEL = 'Normalized Response (a.u.)'
LABEL_FONTSIZE = 12
LEGEND_FONTSIZE = 8
LEGEND_LABEL_SPACING = 0.4 # line spacing between adjacent legend labels
LEGEND_LOCATION = 'best' # one of the following: 'best' / 'upper right' / 'upper left' / 'lower left' / 'lower right' / 'right' / 'center left' / 'center right' / 'lower center' / 'upper center' / 'center'
LINE_WIDTH = 1.5
LINE_MARKER = '-' # solid '-'; dash '--'; dash dot '-.'; dot ':'
FIG_SIZE = (4, 3) # width and height, in inches
FIG_DPI_DISPLAY = 96 # dots per inch for display
FIG_DPI_SAVE = 300 # dots per inch for saving as png
SAVE_TYPES = 'ask' # output file types to save at the end: can be '' (nothing); 'ask' (will ask for user input); one of the following: 'png', 'svg', 'csv', and 'npy'; or a combination of the previous four types, e.g., 'png csv'
SAVE_FILENAME = 'dir|output_|datetime:%Y-%m-%d-%H-%M-%S|_|gpcname|GPC' # output filename without extension: can be a plain-text path (either relative or absolute), e.g. 'C:/output'; or if it contains '|', the parsing rules are as follows: If the first element is 'dir', the saving path is the same as that of the first input file; if one of the elements is 'datetime:{format}', it will be replaced by the current datetime in the provided format; if one of the elements is 'gpcname', it will be replaced by the value of `GPCNAME` (e.g., 'DMF'); all elements will be concatenated in the end 
BASELINE_ASK = True # whether to ask user when a valid baseline is provided; when False, baseline is always applied silently
BASELINE_PARAMS = (False, '!baseline!', 1.0) # a tuple, (Boolean: always, String: filename, Float: factor)
# - always: when True, the app will always apply the baseline provided by the `filename` element; when False, the app will only apply the baseline when the baseline file (in the name specified in the `filename` element) is present in the input arguments
# - filename: when `always==True`, this is a relative file path of the baseline data file (please include the extension name); when `always==False`, this is a base name of the baseline data file (please do not include the extension name), and if the file whose name matches with it is passed to the app via input arguments, the baseline will be applied
# - factor: when 0, this function is turned off regardless of other two elements; otherwise, the baseline magnitude will be multiplied by this factor, which will be subtracted from other GPC traces
# for example, (False, '!baseline!', 1.0) means: if a '!baseline!.csv' or '!baseline!.npy' or ... is dragged onto this app, all GPC traces will be subtracted by the baseline data provided in that file

PLT_RCPARAMS = { # fine-tune matplotlib configs here
    'font.family': 'Arial', # default font
    'mathtext.fontset': 'custom',
    'mathtext.rm': 'Arial', # use Arial for displaying LaTeX formula
    'mathtext.bf': 'Arial:bold', # use \bf{} to make font bold
    'mathtext.it': 'Arial:italic', # use \it{} to make font italic
    'mathtext.tt': 'Arial:bold:italic', # use \tt{} to make font bold italic
    'axes.labelsize': LABEL_FONTSIZE,
    'legend.loc': LEGEND_LOCATION,
    'legend.fontsize': LEGEND_FONTSIZE,
    'legend.labelspacing': LEGEND_LABEL_SPACING,
    'lines.linewidth': LINE_WIDTH,
    'svg.fonttype': 'none' # do not create outlines for texts
}

BKGROUND_TYPE = 'Akima' # default background fitting method: can be 'Akima' (Akima 1D interpolator) / 'Spline' (cubic spline interpolator) / 'Linear'
BKGROUND_SAVE = None # what file types to save after the background is subtracted: can be None (ask) / 0 (do not save) / 1 (save as csv) / 2 (save as npy) / 3 (save both)
