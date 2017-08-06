import pytest

from tests.conftest import FakeCurses

from splutter.window import Window


class TestCursesWindow(object):
    """Fake curses window to make rendering calls against.

    Records rendering calls so they can be verified later.
    """
    def __init__(self):
        self._buffer = [['' for i in range(100)] for j in range(100)]
        print(self._buffer)

    def refresh(self):
        pass

    def erase(self):
        pass

    def addstr(self, y, x, char, attr):
        print(y, x, char, attr)

    def addch(self, y, x, char, attr):
        pass

    def getch(self):
        pass


    def addch(self, y, x, char, attr):
        pass


@pytest.fixture
def window():
    ncurses_window = TestCursesWindow()
    window = Window(ncurses_window, curses_lib=FakeCurses())
    return window


class TestBasicDrawing(object):
    def test_basic_string(self, window):
        window.add_string(0, 0, "foo bar baz")
