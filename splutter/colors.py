import curses
import logging


_COLOR_UID = 1

BLACK = curses.COLOR_BLACK
WHITE = curses.COLOR_WHITE


class Color(object):
    def __init__(self, fg=WHITE, bg=BLACK):
        global _COLOR_UID
        self.COLOR_UID = _COLOR_UID
        _COLOR_UID += 1
        self._fg = fg
        self._bg = bg
        self.flush()

    def change_color(self, fg=None, bg=None, flush=True):
        self._fg = fg if fg is not None else self._fg
        self._bg = bg if bg is not None else self._bg
        if flush:
            self.flush()

    def flush(self):
        logging.error('Assigning %d, %d, %d',
                      self.COLOR_UID, self._fg, self._bg)
        curses.init_pair(self.COLOR_UID, self._fg, self._bg)


LIGHT_GRAY = 237
LIGHT_GREY = LIGHT_GRAY
