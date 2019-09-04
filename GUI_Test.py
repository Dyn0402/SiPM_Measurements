#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on September 03 7:20 PM 2019
Created in PyCharm
Created as SiPM_Measurements/GUI_Test.py

@author: Dylan Neff, dylan
"""

from tkinter import *
from tkinter import filedialog


def main():
    window = Tk()
    window.title("SiPM IV Measurements")
    window.geometry('600x400')

    out_dir_lbl = Label(window, text='Output Directory: ')
    out_dir_lbl.grid(column=0, row=0)
    out_dir_field = Label(window, text='')
    out_dir_field.grid(column=1, row=0)
    out_dir_btn = Button(window, text='Change Output Directory', command=lambda: change_out_dir(out_dir_field))
    out_dir_btn.grid(column=2, row=0)

    start_v_lbl = Label(window, text='Start Voltage')
    start_v_lbl.grid(column=0, row=1)
    start_v_field = Label(window, text='')
    start_v_field.grid(column=1, row=1)
    start_v_entry = Entry(window, width=20)
    start_v_entry.grid(column=2, row=1)
    start_v_btn = Button(window, text='Change Start Voltage',
                         command=lambda: change_start_v(start_v_field, start_v_entry.get()))
    start_v_btn.grid(column=3, row=1)

    board_id_lbl = Label(window, text='Board ID')
    board_id_lbl.grid(column=0, row=2)
    board_id_field = Label(window, text='')
    board_id_field.grid(column=1, row=2)
    board_id_entry = Entry(window, width=20)
    board_id_entry.grid(column=2, row=2)
    board_id_btn = Button(window, text='Change Board ID',
                          command=lambda: change_board_id(board_id_field, board_id_entry.get()))
    board_id_btn.grid(column=3, row=2)

    sound_chk_state = BooleanVar()
    sound_chk_state.set(True)
    sound_chk = Checkbutton(window, text='Beep on Completion?', var=sound_chk_state)
    sound_chk.grid(column=1, row=5)
    quit_btn = Button(window, text='Quit', command=window.destroy)
    quit_btn.grid(column=4, row=5)

    gui_data = {'start_v_field': start_v_field, 'start_v_entry': start_v_entry,
                'board_id_field': board_id_field, 'board_id_entry': board_id_entry,
                'out_dir_field': out_dir_field, 'sound_chk_state': sound_chk_state}

    start_btn = Button(window, text='Start', command=lambda: start_measurement(gui_data))
    start_btn.grid(column=0, row=5)
    window.mainloop()
    print('donzo')


def change_out_dir(out_dir_field):
    out_dir = filedialog.askdirectory()
    out_dir_field.configure(text=out_dir)


def change_start_v(start_v_field, new_start_v):
    start_v_field.configure(text=new_start_v)


def change_board_id(board_id_field, new_board_id):
    board_id_field.configure(text=new_board_id)


def start_measurement(gui_data):
    print(gui_data['out_dir_field'].cget('text'))


if __name__ == '__main__':
    main()
