import datetime
import tkinter as tk
from tkinter import *
from tkinter import ttk

import numpy as np


def data_input_popup(date, shoes, mileage):
    # Creating tkinter window
    window = tk.Tk()
    window.geometry('350x350')

    ttk.Label(window,
              text=f'Enter data for {mileage:.2f} mile run on\n{date.strftime("%A, %b %d %Y")}',
              font=("Times New Roman", 10)).grid(
        column=0, row=10, padx=10, pady=25)
    sho = tk.StringVar(window, 'catchall')
    ttk.Label(window, text="Shoes Worn :", font=("Times New Roman", 10)).grid(column=0, row=15, padx=10, pady=5)
    shoe_menu = ttk.OptionMenu(window, sho, '', *shoes)
    shoe_menu.grid(column=1, row=15)

    ttk.Label(window, text='Liters Consumed :', font=("Times New Roman", 10)).grid(column=0, row=16, padx=10, pady=5)
    liter_num = tk.DoubleVar(value=0.)
    liter_entry = ttk.Entry(window, textvariable=liter_num)
    liter_entry.grid(column=1, row=16)

    ttk.Label(window, text='Calories Consumed :', font=("Times New Roman", 10)).grid(column=0, row=17, padx=10, pady=5)
    cal_num = tk.DoubleVar(value=0.)
    calnum_entry = ttk.Entry(window, textvariable=cal_num)
    calnum_entry.grid(column=1, row=17)

    ttk.Label(window, text='Calorie Description :', font=("Times New Roman", 10)).grid(column=0, row=18, padx=10,
                                                                                       pady=5)
    cal_desc = tk.StringVar()
    caldesc_entry = ttk.Entry(window, textvariable=cal_desc)
    caldesc_entry.grid(column=1, row=18)

    ttk.Label(window, text='Start Weight (lb) :', font=("Times New Roman", 10)).grid(column=0, row=19, padx=10, pady=5)
    # strtw_num = tk.DoubleVar(value=math.nan)
    strtw_entry = ttk.Entry(window)
    strtw_entry.grid(column=1, row=19)

    ttk.Label(window, text='End Weight (lb) :', font=("Times New Roman", 10)).grid(column=0, row=20, padx=10, pady=5)
    # endw_num = tk.DoubleVar(value=math.nan)
    endw_entry = ttk.Entry(window)
    endw_entry.grid(column=1, row=20)

    def close_window():
        global shoes_worn
        global liters_consumed
        global start_weight_lb
        global end_weight_lb
        global calories_consumed
        global calorie_description
        shoes_worn = sho.get()
        if liter_entry.get() == '':
            liters_consumed = np.nan
        else:
            liters_consumed = float(liter_entry.get())
        if calnum_entry.get() == '':
            calories_consumed = np.nan
        else:
            calories_consumed = float(calnum_entry.get())
        if caldesc_entry.get() == '':
            calorie_description = np.nan
        else:
            calorie_description = caldesc_entry.get()
        if strtw_entry.get() == '':
            start_weight_lb = np.nan
        else:
            start_weight_lb = float(strtw_entry.get())
        if endw_entry.get() == '':
            end_weight_lb = np.nan
        else:
            end_weight_lb = float(endw_entry.get())

        window.destroy()

    button = Button(window, text='Ok', command=close_window)
    button.grid(row=25, column=1)

    window.mainloop()

    return shoes_worn, liters_consumed, start_weight_lb, end_weight_lb, calories_consumed, calorie_description


if __name__ == '__main__':
    date = datetime.datetime.today()
    shoes = ['Hoka', 'Kinvara', 'Other']

    shoes_worn = 'catchall'
    liters_consumed = 0.
    start_weight_lb = np.nan
    end_weight_lb = np.nan

    sh, lc, sw, ew, cc, cd = data_input_popup(date, shoes, 5.2)
    print(f'shoes: {sh}, liters: {lc}, start weight: {sw}, end weight: {ew}, cal_cons: {cc}, cal_desc: {cd}')
    a = 1
