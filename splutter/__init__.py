import os
import curses
from contextlib import contextmanager

from splutter.keys import *  # noqa
from splutter.window import Window
from splutter.core import View
from splutter.core import Controller
from splutter.art import Border

ESCDELAY = '25'


def init():
    os.environ.setdefault('ESCDELAY', ESCDELAY)
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    screen.keypad(1)
    curses.start_color()
    screen.nodelay(1)
    return Window(screen)


def cleanup(window):
    curses.nocbreak()
    window.curses_window.keypad(0)
    curses.echo()
    curses.endwin()


@contextmanager
def splutter_window():
    try:
        screen = init()
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
