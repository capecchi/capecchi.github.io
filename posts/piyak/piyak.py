import numpy as np
import pylab as pl
from mpmath import mp
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gridspec
import matplotlib.colorbar as cbar

mpl.use('TkAgg')  # allows plotting in debug mode


# representation of a number in a given base
def digify2(num_digits, which_num='pi', base: int = 2):
    fig = plt.figure(f'{which_num} representation in base-{base}', figsize=(25, 6))
    plt.rcParams.update({'font.size': 18})
    ax = fig.add_subplot(111)
    mp.dps = num_digits + 1
    if which_num == 'pi':
        number = mp.pi

    pwr_strt = 0
    while base ** pwr_strt <= number:  # brings pwr s.t. base**pwr > number
        pwr_strt += 1
    while base ** pwr_strt > number:  # get first pwr s.t. base**pwr <= number
        pwr_strt -= 1
    num_str = ''
    pwr = int(pwr_strt)
    while pwr > pwr_strt - num_digits:
        count = int(np.floor(number / base ** pwr))
        col = 1 - count / (base - 1)
        ax.fill_between([pwr - .5, pwr + .5], [0, 0], [1, 1], facecolor=str(col))
        number -= count * base ** pwr
        num_str += str(count)
        if pwr == 0:
            num_str += '.'
        pwr -= 1

    cax, _ = cbar.make_axes(ax)
    cb = cbar.ColorbarBase(cax, cmap=mpl.colors.ListedColormap([str(s) for s in np.linspace(1, 0, num=base)]),
                           norm=mpl.colors.Normalize(vmin=-.5, vmax=base - .5), ticks=np.arange(base))
    cb.set_label('Count')
    ax.set_xlabel('Base Power')
    ax.set_xlim(ax.get_xlim()[::-1])
    ax.set_yticks([])
    ax.set_title(f'{which_num} representation in base: {base}\n{num_str}')
    # plt.tight_layout()


# Representation of the BASE 10 DIGITS of a number in a different base
def digify(num_digits, number='pi', base: int = 2):
    num_str = ''
    fig = plt.figure(f'Base 10 digits of {number}, representation in base-{base}', figsize=(25, 6))
    plt.rcParams.update({'font.size': 18})
    ax = fig.add_subplot(111)
    mp.dps = num_digits + 1
    if number == 'pi':
        num_str = str(mp.pi)
    max_power = int(np.floor(1 / np.log10(base)))
    num_str = ''.join(num_str.split('.'))  # remove period
    digits = [int(n) for n in num_str]
    for i, dig in enumerate(digits):
        dig_decr = int(dig)
        while dig_decr > 0:
            pwr = 0
            while base ** (pwr + 1) <= dig_decr:
                pwr += 1
            count = int(np.floor(dig_decr / base ** pwr))
            col = 1 - count / (base - 1)
            ax.fill_between([i + .5, i + 1.5], [pwr - .5, pwr - .5], [pwr + .5, pwr + .5], facecolor=str(col))
            dig_decr -= count * base ** pwr

    cax, _ = cbar.make_axes(ax)
    cb = cbar.ColorbarBase(cax, cmap=mpl.colors.ListedColormap([str(s) for s in np.linspace(1, 0, num=base)]),
                           norm=mpl.colors.Normalize(vmin=-.5, vmax=base - .5), ticks=np.arange(base))
    cb.set_label('Count')
    ax.set_xlabel('Digit')
    ax.set_ylabel('Base Power')
    ax.set_title(f'Base 10 digits of {number}, representation in base-{base}')
    ax.set_yticks(np.arange(0, max_power + 1, 1))


if __name__ == '__main__':
    # digify(30, base=2)
    # digify(30, base=4)
    # digify(30, base=3)
    digify2(50, base=2)

    plt.show()
