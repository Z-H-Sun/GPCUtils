# GPC-specific settings
# Note: settings here will override the settings in `config.py`

# GPC_NAME = GPC's name (can be set as part of output filename)
# NOR_MRANGE = the range of data to normalize
# HEADER_X, HEADER_Y = headers of interest in the GPC data files
# DELIMITER = char that separates values in input files (comma or tab)
# ALLOW_NEG_NORM = whether to allow normalization to range [-1, 0] instead of [0, 1], which is useful when there is a predominant negative peak (e.g., PDMS in chloroform)

# general settings for THF GPC
"""
GPC_NAME = 'THF'
NORM_RANGE = (14, 28)
HEADER_X = 'Retention time'
HEADER_Y = 'rid1A/ELU'
DELIMITER = '\t'
ALLOW_NEG_NORM = False
"""

# general settings for DMF GPC
"""
GPC_NAME = 'DMF'
NORM_RANGE = (10, 18)
HEADER_X = 'time (min)'
HEADER_Y = 'differential refractive index data: differential refractive index  (RIU)'
DELIMITER = ','
ALLOW_NEG_NORM = False
"""

# general settings for chloroform GPC
#"""
GPC_NAME = 'CF'
NORM_RANGE = (5, 13)
HEADER_X = 'X:'
HEADER_Y = 'Y:'
DELIMITER = '\t'
ALLOW_NEG_NORM = True
BASELINE_PARAMS = (True, 'CFbaseline.tsv', 0.8) # for all chloroform GPC traces, always subtract them by a baseline provided by 'baselineCF.tsv' in the same folder as this app (whose magnitude is multiplied by 0.8)
#"""
