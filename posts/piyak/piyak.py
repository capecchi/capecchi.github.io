import numpy as np
import pylab as pl
from mpmath import mp
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gridspec
import matplotlib.colorbar as cbar


# ACTUAL representation of a number in a given base
def digify2(num_digits, which_num='pi', base: int = 2):
    fig = plt.figure(f'{which_num} representation in base-{base}')
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


# Representation of the BASE 10 DIGITS of a number in a different base
def digify(num_digits, number='pi', base: int = 2):
    num_str = ''
    fig = plt.figure(f'{number} representation in base-{base}')
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
    ax.set_title(f'{number} representation in base-{base}')
    ax.set_yticks(np.arange(0, max_power+1, 1))


def main(num_digits, top=False, e=False, phi=False, euler=False, catalan=False,
         apery=False, khinchin=False, glaisher=False, mertens=False,
         twinprime=False, negate=False, base10=False):
    mp.dps = num_digits + 1
    if e:
        num_str = str(mp.e)
    elif phi:
        num_str = str(mp.phi)
    elif euler:
        num_str = str(mp.euler)
    elif catalan:
        num_str = str(mp.catalan)
    elif apery:
        num_str = str(mp.apery)
    elif khinchin:
        num_str = str(mp.khinchin)
    elif glaisher:
        num_str = str(mp.glaisher)
    elif mertens:
        num_str = str(mp.mertens)
    elif twinprime:
        num_str = str(mp.twinprime)
    else:
        num_str = str(mp.pi)  # '{:49.48f}'.format(np.pi)

    num_str = num_str[0:1] + num_str[2:]  # remove period
    digits = np.array([], dtype=int)
    i = 1
    while len(digits) < num_digits:
        dig = int(num_str[i - 1:i])
        digits = np.append(digits, dig)
        i += 1

    if not base10:
        xx = np.arange(num_digits * 100 + 1) / 100.  # 10 pts per number up to max(digits+1)
        ones = np.ones(len(xx))
        twos = np.ones(len(xx))
        fours = np.ones(len(xx))
        eights = np.ones(len(xx))

        place = np.arange(len(digits))
        for i in place:
            dig = digits[i]
            bit = "{0:b}".format(dig)
            while len(bit) < 4:
                bit = "0" + bit
            imax = np.max(np.where(xx <= i + 1)) + 1
            imin = np.min(np.where(xx >= i))
            ones[imin:imax] = ones[imin:imax] * int(bit[3:4])
            twos[imin:imax] = twos[imin:imax] * int(bit[2:3])
            fours[imin:imax] = fours[imin:imax] * int(bit[1:2])
            eights[imin:imax] = eights[imin:imax] * int(bit[0:1])

        if negate:
            ones = abs(ones - 1)
            twos = abs(twos - 1)
            fours = abs(fours - 1)
            eights = abs(eights - 1)

        if not top:  # ones on bottom
            off1 = 0
            off2 = 1
            off4 = 2
            off8 = 3
        if top:  # ones on top
            off1 = 3
            off2 = 2
            off4 = 1
            off8 = 0

        fig, ax = pl.subplots()
        ax.fill_between(xx, xx * 0 + off8, eights + off8, facecolor='black')
        ax.fill_between(xx, xx * 0 + off4, fours + off4, facecolor='black')
        ax.fill_between(xx, xx * 0 + off2, twos + off2, facecolor='black')
        ax.fill_between(xx, xx * 0 + off1, ones + off1, facecolor='black')
        pl.show()

    if base10:
        xx = np.arange(num_digits * 100 + 1) / 100.  # 10 pts per number up to max(digits+1)
        ones = np.ones(len(xx))
        twos = np.ones(len(xx))
        threes = np.ones(len(xx))
        fours = np.ones(len(xx))
        fives = np.ones(len(xx))
        sixes = np.ones(len(xx))
        sevens = np.ones(len(xx))
        eights = np.ones(len(xx))
        nines = np.ones(len(xx))

        place = np.arange(len(digits))
        for i in place:
            dig = digits[i]
            imax = np.max(np.where(xx <= i + 1)) + 1
            imin = np.min(np.where(xx >= i))

            if dig != 1: ones[imin:imax] = ones[imin:imax] * 0
            if dig != 2: twos[imin:imax] = twos[imin:imax] * 0
            if dig != 3: threes[imin:imax] = threes[imin:imax] * 0
            if dig != 4: fours[imin:imax] = fours[imin:imax] * 0
            if dig != 5: fives[imin:imax] = fives[imin:imax] * 0
            if dig != 6: sixes[imin:imax] = sixes[imin:imax] * 0
            if dig != 7: sevens[imin:imax] = sevens[imin:imax] * 0
            if dig != 8: eights[imin:imax] = eights[imin:imax] * 0
            if dig != 9: nines[imin:imax] = nines[imin:imax] * 0

        clrs = ['white', 'red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'magenta', 'saddlebrown', 'black']

        if 0:  # grayscale
            aa = np.arange(10) / 9
            clrs_str = [str(s) for s in aa]
            clrs = clrs_str

        fig, ax = pl.subplots()
        ax.fill_between(xx, xx * 0, ones, facecolor=clrs[1])
        ax.fill_between(xx, xx * 0, twos, facecolor=clrs[2])
        ax.fill_between(xx, xx * 0, threes, facecolor=clrs[3])
        ax.fill_between(xx, xx * 0, fours, facecolor=clrs[4])
        ax.fill_between(xx, xx * 0, fives, facecolor=clrs[5])
        ax.fill_between(xx, xx * 0, sixes, facecolor=clrs[6])
        ax.fill_between(xx, xx * 0, sevens, facecolor=clrs[7])
        ax.fill_between(xx, xx * 0, eights, facecolor=clrs[8])
        ax.fill_between(xx, xx * 0, nines, facecolor=clrs[9])
        pl.show()


if __name__ == '__main__':
    # main(30)
    # main(30, base10=True)
    # digify(30, base=3)
    # digify(30, base=4)
    # digify2(30, base=3)
    digify2(50, base=2)
    plt.show()
