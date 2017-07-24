import os
import argparse
import asyncio

import splutter
from splutter import splutter_window
from splutter.core import View
from splutter.core import Controller
from splutter.exceptions import CloseSplutterWindow
from splutter.art import Art
from splutter.art import Border
from splutter.art import TextField


ART = r"""
  _--_                                     _--_
/#()# #\         0             0         /# #()#\
|()##  \#\_       \           /       _/#/  ##()|
|#()##-=###\_      \         /      _/###=-##()#|
 \#()#-=##  #\_     \       /     _/#  ##=-#()#/
  |#()#--==### \_    \     /    _/ ###==--#()#|
  |#()##--=#    #\_   \!!!/   _/#    #=--##()#|
   \#()##---===####\   O|O   /####===---##()#/
    |#()#____==#####\ / Y \ /#####==____#()#|
     \###______######|\/#\/|######______###/
        ()#O#/      ##\_#_/##      \#O#()
       ()#O#(__-===###/ _ \###===-__)#O#()
      ()#O#(   #  ###_(_|_)_###  #   )#O#()
      ()#O(---#__###/ (_|_) \###__#---)O#()
      ()#O#( / / ##/  (_|_)  \## \ \ )#O#()
      ()##O#\_/  #/   (_|_)   \#  \_/#O##()
       \)##OO#\ -)    (_|_)    (- /#OO##(/
        )//##OOO*|    / | \    |*OOO##\\(
        |/_####_/    ( /X\ )    \_####_\|
       /X/ \__/       \___/       \__/ \X\
      (#/                               \#)
"""


INSTRUCTIONS = r"""Commands:
Q - Quit.
I - Insert mode.
"""


class ArtController(Controller):
    INSERT_MODE = 0
    CONTROL_MODE = 1

    def __init__(self, art):
        super().__init__()
        self._cursor_x = 1
        self._cursor_y = 2
        self._mode = None
        self._art = Art(1, 2, art)
        self._border = Border(0, 1, self._art.width + 1, self._art.height + 1)
        self._mode_text = TextField(1, 0)
        self._stats_text = TextField(1, self._art.bottom + 1,
                                     'Size: %d x %d' % (self._art.width,
                                                        self._art.height))
        self._control_mode_instructions = Art(
            self._border.right + 2, 2, INSTRUCTIONS)

        art_view = View()
        art_view.add_component('view_screen', self._art)
        art_view.add_component('border', self._border)
        art_view.add_component('mode_text', self._mode_text)
        art_view.add_component('stats_text', self._stats_text)
        art_view.add_component('instructions', self._control_mode_instructions)
        self.add_view('art_view', art_view)

        self._set_mode(self.INSERT_MODE)

    def _set_mode(self, mode):
        self._mode = mode
        if mode == self.INSERT_MODE:
            self._mode_text.text = ('Insert mode: press ESC to enter control '
                                    'mode')
            self.get_view('art_view').remove_component('instructions')
        elif mode == self.CONTROL_MODE:
            self._mode_text.text = ('Control mode: press I to enter insert '
                                    'mode')
            self.get_view('art_view').add_component(
                'instructions', self._control_mode_instructions)

    def _in_art_view(self, x, y):
        view = self.get_view('art_view').get_component('view_screen')
        return (view.y <= y < view.height + view.y and
                view.x <= x < view.width + view.x)

    def _try_move(self, dy, dx, window):
        x, y = self._cursor_x + dx, self._cursor_y + dy
        if self._in_art_view(x, y):
            self._cursor_x, self._cursor_y = x, y

    def render(self, window):
        super().render(window)
        window.move_cursor(self._cursor_x, self._cursor_y)

    def _handle_insert_mode_key(self, input_ch, window):
        if input_ch == splutter.KEY_UP:
            self._try_move(-1, 0, window)
        elif input_ch == splutter.KEY_DOWN:
            self._try_move(1, 0, window)
        elif input_ch == splutter.KEY_LEFT:
            self._try_move(0, -1, window)
        elif input_ch == splutter.KEY_RIGHT:
            self._try_move(0, 1, window)
        elif 32 <= input_ch < 128:
            # Ascii range for a printable character. Overwrite the current char
            # in the art box.
            self._art.set_entry(
                self._cursor_x - self._art.x,
                self._cursor_y - self._art.y,
                chr(input_ch))
        elif input_ch == splutter.KEY_ESC:
            self._set_mode(self.CONTROL_MODE)

    def _handle_control_mode_key(self, input_ch, window):
        value = chr(input_ch)
        if value == 'i' or value == 'I':
            self._set_mode(self.INSERT_MODE)
        if value == 'q' or value == 'Q':
            raise CloseSplutterWindow(
                'Exiting because %s was pressed.' % value)

    def handle_key(self, input_ch, window):
        if self._mode == self.INSERT_MODE:
            self._handle_insert_mode_key(input_ch, window)
        elif self._mode == self.CONTROL_MODE:
            self._handle_control_mode_key(input_ch, window)


def _load_art(path):
    with open(path, 'r') as f:
        return f.read()


def _get_filepath():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', required=False, default=None,
                        help='Path to filename to show as an ascii art file')
    args = parser.parse_args()
    if args.filepath:
        args.filepath = os.path.abspath(args.filepath)
    return args.filepath


def main():
    filepath = _get_filepath()
    if filepath:
        art = _load_art(filepath)
    else:
        art = ART
    loop = asyncio.get_event_loop()
    controller = ArtController(art)

    with splutter_window() as window:
        loop.run_until_complete(controller.attach_to_window(window))


if __name__ == '__main__':
    main()
