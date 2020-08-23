import warnings
from .project import *

warnings.filterwarnings("ignore")

pd.set_option('display.float_format', lambda x: '%.4f' % x)

# pd.options.display.float_format = '{:,.10f}'.format
