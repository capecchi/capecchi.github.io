import os
import numpy as np


class BillExcept(Exception):
    def __init__(self, message=None):
        self.message = message


def get_my_direc(append='', err=''):
    if os.path.isdir('C:/Users/Owner'):
        direc = f'C:/Users/Owner/{append}'
    elif os.path.isdir('C:/Users/wcapecch'):
        direc = f'C:/Users/wcapecch/{append}'
    elif os.path.isdir('C:/Users/willi'):
        direc = f'C:/Users/willi/{append}'
    else:
        raise BillExcept(err)
    return direc


def grn_ylw_red_colorscale(maxval=1):
    r = [44, 163, 255, 255, 255]
    g = [186, 255, 244, 167, 0]
    b = [0, 0, 0, 0, 0]
    v = np.linspace(0, maxval, 5)
    cs = [[v[i], f'rgb({r[i]},{g[i]},{b[i]})'] for i in range(5)]
    cs.append([1, 'rgb(255,0,0)'])
    return cs
