from curses.textpad import rectangle

from splutter.core import Component


class Art(Component):
    def __init__(self, x, y, raw_source, bind_to=Component.BIND_TOP_LEFT):
        super().__init__(x, y, bind_to=bind_to)
        self._bind_to = bind_to
        self._raw_source = raw_source
        self._width = 0
        self._height = 0
        self._lines = []
        self.set_lines(raw_source)

    @property
    def width(self):
        return self._width

    def _render(self, x, y, window):
        y_offset = y
        for line in self._lines:
            window.add_string(x, y_offset, line.rstrip())
            y_offset += 1

    def _pad(self, line):
        length = len(line)
        pad_right_length = self._width - length
        return '%s%s' % (line, ' ' * pad_right_length)

    def set_entry(self, x, y, char):
        line = self._pad(self._lines[y])
        new_line = '%s%s%s' % (line[:x], char, line[x+1:])
        self._lines[y] = new_line

    def set_lines(self, raw_source):
        self._lines = raw_source.split('\n')
        self._height = len(self._lines)
        self._width = 0
        for line in self._lines:
            self._width = max(self._width, len(line))

    def move(self, x=None, y=None):
        if x is None:
            x = self._x
        if y is None:
            y = self._y
        self._x = x
        self._y = y


class Border(Component):
    def __init__(self, x, y, w, h):
        super().__init__(x, y)
        self._width = w
        self._height = h

    def _render(self, x, y, window):
        rectangle(window.curses_window,
                  y, x, y + self._height, self._x + self._width)
