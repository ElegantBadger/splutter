from splutter.core import Component
from splutter.keys import KEY_LEFT, KEY_RIGHT, KEY_DOWN, KEY_UP, KEY_ENTER, \
    KEY_DELETE, KEYS_ARROW


class TextField(Component):
    def __init__(self, x, y, width=12, max_length=None, text='',
                 bind_to=Component.BIND_TOP_LEFT):
        super().__init__(x, y, bind_to=bind_to)
        self._max_width = width
        if max_length is None:
            max_length = width
        self._max_length = max_length
        self._x_offset = len(text)
        self._text_offset = 0
        self._text = text
        self._left_boundry = 0

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new_text):
        self._text = new_text

    def _text_window(self):
        """Get the window of the text that should be visible."""
        start = self._left_boundry
        end = start + self._max_width
        return self._text[start:end+1]

    def _render(self, x, y, window):
        window.add_string(x, y, self._text_window())

    def _move(self, dx):
        self._x_offset = min(max(self._x_offset + dx, 0), len(self._text))
        self._recalculate_boundary()

    def _handle_arrow(self, event, window):
        if event == KEY_LEFT:
            self._move(-1)
        elif event == KEY_RIGHT:
            self._move(1)

    def _handle_delete(self):
        if self._x_offset == 0:
            return
        new_text = '%s%s' % (self._text[:self._x_offset-1],
                             self._text[self._x_offset:])
        self._x_offset -= 1
        self._text = new_text
        self._recalculate_boundary()

    def _recalculate_boundary(self):
        if self._cursor_location() > self._max_width:
            self._left_boundry += 1

        if self._cursor_location() < 0:
            self._left_boundry -= 1

        if self._left_boundry < 0:
            self._left_boundry = 0

    def _handle_printable(self, printable, event, window):
        if len(self._text) > self._max_length:
            return
        new_text = '%s%s%s' % (self._text[:self._x_offset],
                               printable,
                               self._text[self._x_offset:])
        self.text = new_text
        self._x_offset += 1
        self._recalculate_boundary()

    def _handle_enter(self):
        """Action to perform when enter is pressed.

        This is intended to be overriden by subclasses if they want to do
        something on enter.
        """
        pass

    def handle_event(self, event, window):
        if event in KEYS_ARROW:
            self._handle_arrow(event, window)
        elif event == KEY_DELETE:
            self._handle_delete()
        elif event == KEY_ENTER:
            self._handle_enter()
        else:
            printable = event.printable()
            if printable:
                self._handle_printable(printable, event, window)

    def _cursor_location(self):
        return self._x_offset - self._left_boundry

    def has_focus(self, x, y, window):
        window.move_cursor(x + self._cursor_location() + self.x,
                           y + self.y)
