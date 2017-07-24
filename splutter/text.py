from splutter.core import Component
from splutter.keys import KEY_LEFT, KEY_RIGHT, KEY_DOWN, KEY_UP, KEY_ENTER, \
    KEY_DELETE, KEYS_ARROW


class TextField(Component):
    def __init__(self, x, y, width=12, text='', multiline=False,
                 bind_to=Component.BIND_TOP_LEFT):
        super().__init__(x, y, bind_to=bind_to)
        self._max_width = width
        self._x_offset = len(text)
        self._y_offset = 0
        self._text = text
        self._multiline = multiline

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new_text):
        self._text = new_text

    def _render(self, x, y, window):
        window.add_string(x, y, self._text)

    def _move(self, dx, dy):
        if self._multiline is False:
            dy = 0
        self._x_offset = min(max(self._x_offset + dx, 0), len(self._text))
        self._y_offset = min(max(self._y_offset + dy, 0), 1)

    def _handle_arrow(self, event, window):
        if event == KEY_LEFT:
            self._move(-1, 0)
        elif event == KEY_RIGHT:
            self._move(1, 0)
        elif event == KEY_UP:
            self._move(0, -1)
        elif event == KEY_DOWN:
            self._move(0, 1)

    def _handle_delete(self):
        if self._x_offset == 0:
            return
        new_text = '%s%s' % (self._text[:self._x_offset-1],
                             self._text[self._x_offset:])
        self._x_offset -= 1
        self._text = new_text

    def _handle_printable(self, printable, event, window):
        new_text = '%s%s%s' % (self._text[:self._x_offset],
                               printable,
                               self._text[self._x_offset:])
        if len(new_text) > self._max_width:
            return
        self._x_offset += 1
        self._text = new_text

    def handle_enter(self, event, window):
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

    def has_focus(self, x, y, window):
        window.move_cursor(x + self._x_offset + self.x,
                           y + self._y_offset + self.y)
