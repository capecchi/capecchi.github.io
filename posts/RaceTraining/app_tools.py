import numpy as np
import datetime
import tkinter as tk
from tkinter import *
from tkinter import ttk

import numpy as np
import stravalib.exc
from stravalib.client import Client


def get_client(code):
    client_id = 34049
    client_secret = '2265a983040000b3b865a0fc333f41cd701dcb5f'

    client = Client()
    client.authorization_url(34049, 'http://localhost:8080', scope='activity:read_all')
    token_response = client.exchange_code_for_token(client_id, client_secret, code)
    client.access_token = token_response['access_token']
    client.refresh_token = token_response['refresh_token']
    return client


def get_activities(client, after=datetime.date.today() - datetime.timedelta(days=7), before=datetime.date.today()):
    activities = client.get_activities(after=after, before=before)
    try:
        activities = list(activities)
        activities = activities[::-1]  # reverse order so they're chronological
        return activities
    except stravalib.exc.Fault:
        return None


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
