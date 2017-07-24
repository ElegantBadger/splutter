from splutter.core import Component
from splutter.colors import Color
from splutter.colors import WHITE, LIGHT_GRAY
from splutter.keys import KEY_UP
from splutter.keys import KEY_DOWN


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

    def render(self, x, y, window):
        window.add_string(x, y, self._title)


class TableRow(object):
    def __init__(self, data=None):
        if data is None:
            data = []
        self._data = data

    def __iter__(self):
        yield from self._data

    def extend(self, more):
        self._data.extend(more)


class Table(Component):
    DEFAULT_SELECTED_BG_COLOR = LIGHT_GRAY

    def __init__(self, x, y, col_specs, bg_color=None):
        super().__init__(x, y)
        if bg_color is None:
            bg_color = self.DEFAULT_SELECTED_BG_COLOR
        self._col_specs = col_specs
        self._width = sum(s.max_width for s in col_specs)
        self._rows = []
        self._selected = 0
        self._selected_color = Color(fg=WHITE, bg=bg_color)

    def up(self):
        self._selected = max(0, self._selected - 1)

    def down(self):
        self._selected = max(len(self._rows), self._selected + 1)

    @property
    def selected_row(self):
        return self._rows[self._selected]

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, rows):
        self._rows = rows
        self._height = len(self._col_specs) + 1
        self._selected = min(self._selected, len(self._rows) - 1)

    def _render(self, x, y, window):
        x_offset = x
        y_offset = y
        for col_spec in self._col_specs:
            col_spec.render(x_offset, y_offset, window)
            x_offset += col_spec.max_width + 1

        y_offset += 1
        x_offset = x
        for i, row in enumerate(self._rows):
            for col, spec in zip(row, self._col_specs):
                col = str(col)
                color = None
                if i == self._selected:
                    color = self._selected_color
                else:
                    color = window.default_color
                window.add_string(x_offset, y_offset, col, color)
                right_pad = ' ' * spec.trailing_space(col)
                window.add_string(x_offset + len(col), y_offset, right_pad,
                                  color)
                x_offset += spec.max_width + 1
            x_offset = x
            y_offset += 1

    def has_focus(self, x, y, window):
        window.move_cursor(self.right + x, self._selected + self.y + y + 1)

    def _handle_event(self, event, delta_select):
        max_select = len(self._rows) - 1
        self._selected = min(max(self._selected + delta_select, 0), max_select)
        event.stop_propagation()

    def handle_event(self, event, window):
        if event == KEY_UP:
            self._handle_event(event, -1)
        elif event == KEY_DOWN:
            self._handle_event(event, 1)
