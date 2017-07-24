import curses
import string

from splutter.colors import Color
from splutter.keys import KEY_ESC


_PRINTABLE_SET = set(string.printable)


class Window(object):
    def __init__(self, window, default_color=None):
        self._window = window
        if default_color is None:
            default_color = Color()
        self._close_reason = None
        self._color = None
        self.default_color = default_color
        self.set_color(default_color)
        self.cursor_location = (None, None)

    def set_color(self, color):
        self._color = color

    @property
    def close_reason(self):
        return self._close_reason

    @close_reason.setter
    def close_reason(self, reason):
        self._close_reason = reason

    @property
    def curses_window(self):
        return self._window

    def erase(self):
        self._window.erase()

    def refresh(self):
        self._window.refresh()

    def add_string(self, x, y, string, color=None):
        if color is None:
            color = self._color
        attr = curses.color_pair(color.COLOR_UID)
        self._window.addstr(y, x, string, attr)

    def add_char(self, x, y, char, color=None):
        if color is None:
            color = self._color
        attr = curses.color_pair(color.COLOR_UID)
        self._window.addch(y, x, char, attr)

    def _create_event_from_code(self, code):
        if code < 0:
            return None
        if code == KEY_ESC:
            real_key = self._window.getch()
            return WindowEvent(real_key, WindowEvent.KEY_EVENT, modifier=code)
        return WindowEvent(code, WindowEvent.KEY_EVENT)

    def get_event(self):
        """Get an event from the window system."""
        input_ch = self._window.getch()
        event = self._create_event_from_code(input_ch)
        return event

    def get_cursor_location(self):
        y, x = self._window.getyx()
        return x, y

    def move_cursor(self, x, y):
        self.cursor_location = (x, y)

    def update_cursor(self):
        x, y = self.cursor_location
        if x is not None and y is not None:
            self._window.move(y, x)
            self._window.cursyncup()


class WindowEvent(object):
    KEY_EVENT = 1
    MOUSE_EVENT = 2

    def __init__(self, code, event_type, modifier=None):
        self._propagate = True
        self._code = code
        self._event_type = event_type
        self._modifier = modifier

    def stop_propagation(self):
        self._propagate = False

    @property
    def should_handle(self):
        return self._propagate

    def __hash__(self):
        return self._code

    def __eq__(self, other):
        if isinstance(other, WindowEvent):
            return self._code == other._code
        elif isinstance(other, int):
            return self._code == other
        elif isinstance(other, str):
            return chr(self._code).lower() == other.lower()
        return False

    def printable(self):
        """Return a printable character if possible."""
        strcode = chr(self._code)
        if set(strcode).issubset(_PRINTABLE_SET):
            return strcode
        return None

    def __neq__(self, other):
        return not self == other


class EventBus(object):
    def __init__(self, controller):
        self._controller = controller

    def propagate_event(self, event, top_view, window):
        """Propagate an event down to the base level view.

        An event first trickles down to the bottom level view, and then
        bubbles back up the view stack, and lastly calls the handle_event
        method defined on the parent controller.
        """
        stack = top_view.get_active_component_stack([])
        for component in reversed(stack):
            if component is not None and event.should_handle:
                component.handle_event(event, window)
        if event.should_handle:
            self._controller.handle_event(event, window)
