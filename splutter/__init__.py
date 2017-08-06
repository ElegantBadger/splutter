import os
import curses
from contextlib import contextmanager

from splutter.keys import *  # noqa
from splutter.window import Window
from splutter.core import View
from splutter.core import Controller
from splutter.art import Border

ESCDELAY = '25'


def init(curses_lib=curses):
    os.environ.setdefault('ESCDELAY', ESCDELAY)
    screen = curses_lib.initscr()
    curses_lib.noecho()
    curses_lib.cbreak()
    screen.keypad(1)
    curses_lib.start_color()
    screen.nodelay(1)
    return Window(screen)


def cleanup(window, curses_lib=curses):
    curses_lib.nocbreak()
    window.curses_window.keypad(0)
    curses_lib.echo()
    curses_lib.endwin()


@contextmanager
def splutter_window(curses_lib=curses):
    try:
        screen = init(curses_lib)
        yield screen
    finally:
        close_reason = None
        if 'screen' in locals():
            cleanup(screen)
            close_reason = screen.close_reason
        if close_reason:
            print(close_reason)


def wrapper(fn, *args, **kwargs):
    curses.wrapper(fn, *args, **kwargs)
