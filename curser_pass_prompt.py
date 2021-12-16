#!/usr/bin/env python3

from typing import Dict, Union

import curses
import os
import random
import re
import yaml


USER = os.environ["USER"]
usr_input = ""


STATUS_ANIMATIONS = {
    'rotating_bar': '|/-\\',
    'snake': '⡇⣆⣤⣰⢸⠹⠛⠏',
    'rolling_box': '⣀⣤⣶⣿⠿⠛⠉',
    'rolling_void': '⣿⠿⣛⣭⣶',
    'survival_1': 'ᚋᚌᚍᚎ',
    'survival_2': 'ᚐᚑᚒᚓ',
    'zen': '࿊࿋࿌',
}
STATUS_ANIMATIONS['random'] = random.choice(list(STATUS_ANIMATIONS.values()))


def get_config() -> Dict[str, Union[str, bool]]:
    cfg = {
        'showCharType': True,
        'animation': 'random',
    }

    config_file_path = os.path.expanduser('~/.config/ucpp/config.yaml')
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as yf:
            usr_cfg = yaml.safe_load(yf)

        if 'showCharType' in usr_cfg:
            assert isinstance(usr_cfg['showCharType'], bool), 'showCharType must be boolean!'
            cfg['showCharType'] = usr_cfg['showCharType']
        if 'animation' in usr_cfg:
            assert usr_cfg['animation'] in STATUS_ANIMATIONS, 'animation must be a one of valid ones!'
            cfg['animation'] = usr_cfg['animation']

    return cfg


def main(stdscr, config):
    global usr_input

    stdscr.clear()
    nlines, ncols = stdscr.getmaxyx()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)

    stdscr.bkgd(' ', curses.color_pair(1) | curses.A_BOLD)
    stdscr.border()

    win_heigh = 5 if config['showCharType'] else 4
    msg = f"Please insert the password for user '{USER}'"
    win = curses.newwin(
        win_heigh, len(msg) + 4, (nlines // 2),
        (ncols // 2) - (len(msg) // 2) -2
    )
    win_nlines, win_ncols = win.getmaxyx()
    win.bkgd(' ', curses.color_pair(2) | curses.A_BOLD)
    win.border()

    win.addstr(1, 2, msg)
    if config['showCharType']:
        hint = 'a  A  0  ?'
        win.addstr(2, (win_ncols // 2) - (len(hint) // 2), hint)

    stdscr.refresh()
    win.refresh()

    lower_status = 0
    upper_status = 0
    number_status = 0
    special_status = 0

    status_mod = STATUS_ANIMATIONS[config['animation']]

    while True:
        status_msg = status_mod[lower_status] + "  " \
            + status_mod[upper_status] + "  " \
            + status_mod[number_status] + "  " \
            + status_mod[special_status]

        win.addstr(
            3 if config['showCharType'] else 2,
            (win_ncols // 2) - (len(status_msg) // 2),
            status_msg
        )
        win.refresh()

        key = win.getkey()
        if key == '\n':
            break

        if re.match("^[a-z]$", key):
            lower_status += 1
            lower_status %= len(status_mod)
        elif re.match("^[A-Z]$", key):
            upper_status += 1
            upper_status %= len(status_mod)
        elif re.match("^[0-9]$", key):
            number_status += 1
            number_status %= len(status_mod)
        else:
            special_status += 1
            special_status %= len(status_mod)

        usr_input += key


if __name__ == '__main__':
    restore_stdout = False

    if 'TTY' in os.environ:
        restore_stdout = True
        os.dup2(1, 113)

        NCURSES_TTY = os.environ['TTY']
        with open(NCURSES_TTY, 'rb') as inf, open(NCURSES_TTY, 'wb') as outf:
            os.dup2(inf.fileno(), 0)
            os.dup2(outf.fileno(), 1)
            os.dup2(outf.fileno(), 2)

    try:
        curses.wrapper(main, get_config())
    finally:
        curses.endwin()

    if restore_stdout:
        os.dup2(113, 1)

    print(usr_input)
