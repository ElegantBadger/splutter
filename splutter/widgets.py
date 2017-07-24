import curses
import curses.textpad


class ColumnSpec(object):
    def __init__(self, title, max_width):
        assert len(title) < max_width
        self._title = title
        self._max_width = max_width

    @property
    def title(self):
        return self._title

    @property
    def max_width(self):
        return self._max_width

    def trailing_space(self, value):
        return self._max_width - len(value)


class TableRow(object):
    def __init__(self, data=None):
        if data is None:
            data = []
        self._data = data

    def __iter__(self):
        yield from self._data

    def extend(self, more):
        self._data.extend(more)

    def action(self, key, websocket):
        raise NotImplementedError('action')


class Table(object):
    BG_HILIGHT = 237

    def __init__(self, x, y, w, h, col_specs):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self._col_specs = col_specs
        self._rows = []
        self._selected = 0

        curses.init_pair(1, curses.COLOR_WHITE, self.BG_HILIGHT)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self._validate()

    def _validate(self):
        """Ensure everything will fit in the table."""
        width = 0
        for col_spec in self._col_specs:
            width += col_spec.max_width
        assert width <= (self.w - 2)

    def set_rows(self, rows):
        self._rows = sorted(rows)

    def action(self, key, websocket):
        """Triggers when a key is sent to the table."""
        if key == curses.KEY_UP:
            self._selected = max(self._selected - 1, 0)
        elif key == curses.KEY_DOWN:
            self._selected = min(self._selected + 1, len(self._rows) - 1)
        else:
            self._rows[self._selected].action(key, websocket)

    def has_focus(self, screen):
        """This is invoked after rendering if the widget has focus."""
        # Starting y location move down for border and header, then down to
        # selected row. x is simply just inside the right edge of the border.
        y = self.y + 2 + self._selected
        x = self.w - 1
        screen.move(y, x)

    def render(self, screen):
        curses.textpad.rectangle(screen, self.y, self.x, self.h, self.w)
        x_offset = self.x + 1
        y_offset = self.y + 1
        for col_spec in self._col_specs:
            screen.addnstr(
                y_offset, x_offset, col_spec.title, col_spec.max_width,
                curses.color_pair(2))
            x_offset += col_spec.max_width

        y_offset += 1
        x_offset = self.x + 1
        for i, row in enumerate(self._rows):
            if i == self._selected:
                attr = curses.color_pair(1)
            else:
                attr = curses.color_pair(2)
            for col, spec in zip(row, self._col_specs):
                col = str(col)
                screen.addnstr(y_offset, x_offset, col, spec.max_width, attr)
                right_pad = ' ' * (spec.trailing_space(col) - 1)
                screen.addstr(y_offset, x_offset + len(col), right_pad, attr)
                x_offset += spec.max_width
            x_offset = self.x + 1
            y_offset += 1
