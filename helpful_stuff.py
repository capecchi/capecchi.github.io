import os


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
