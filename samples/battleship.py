import re
import asyncio
from collections import OrderedDict

from splutter import splutter_window
from splutter.art import Art
from splutter.art import Border
from splutter.core import View
from splutter.core import Controller
from splutter.table import ColumnSpec
from splutter.table import Table
from splutter.keys import KEY_ENTER, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT


_SHIPS_HORIZ = OrderedDict([
    ('Carrier',    '[=====[]==[]==]'),
    ('Battleship', '<=={[]=0}]>'),
    ('Destroyer',  '<==[=()]>'),
    ('Submarine',  '(==(.o)=)'),
    ('Patrol',     '<=(|=>'),
])

_SHIPS_VERT = OrderedDict([
    ('Carrier', '\n'.join(
        ['/=\\',
         '|#|',
         '|#|',
         '[0]',
         '\\=/'])),
    ('Battleship', '\n'.join(
        ['{.}',
         '[=]',
         '[O]',
         '{.}'])),
    ('Destroyer', '\n'.join(
        ['[=]',
         '[O]',
         '[=]'])),
    ('Destroyer', '\n'.join(
        ['/ \\',
         '|0|',
         '\\ /'])),
    ('Patrol', '\n'.join(
        ['/ \\',
         '(\\ /)']))
])


class Ship(Art):
    def __init__(self, x, y, name):
        self._name = name
        self._rotation = 'horizontal'
        super().__init__(x, y, _SHIPS_HORIZ[name])

    def _set_art(self):
        if self._rotation == 'horizontal':
            art = _SHIPS_HORIZ[self._name]
        elif self._rotation == 'vertical':
            art = _SHIPS_VERT[self._name]
        self.set_lines(art)

    def rotate(self):
        if self._rotation == 'horizontal':
            self._rotation = 'vertical'
        elif self._rotation == 'vertical':
            self._rotation = 'horizontal'
        self._set_art()


class BoardView(View):
    SHIP_COMPONENT = 'ship'

    _MOVES = {
        KEY_UP: (0, -1),
        KEY_DOWN: (0, 1),
        KEY_LEFT: (-3, 0),
        KEY_RIGHT: (3, 0)
    }

    def __init__(self):
        super().__init__()
        board = '\n'.join([' ' * 30 for _ in range(10)])
        self._num = 0
        self._board = Art(1, 1, board)
        self._border = Border(0, 0,
                              self._board.width + 1, self._board.height + 1)
        self.add_component('board', self._board)
        self.add_component('border', self._border)
        self.add_component(self.SHIP_COMPONENT, None)
        self.size_to_components()

    def set_ship(self, ship_name):
        """Set the ship that is currently being placed."""
        ship_art = Ship(1, 1, ship_name)
        self.add_component(self.SHIP_COMPONENT, ship_art)

    def _in_bounds(self, component):
        """Force a component back in bounds of the board."""
        component.x = max(1, component.x)
        component.x = min(self.right - component.width, component.x)
        component.y = max(1, component.y)
        component.y = min(self.bottom - component.height, component.y)

    def handle_move_event(self, event, window):
        """Move the currently being placed ship based on a key event."""
        dx, dy = self._MOVES[event]
        ship = self.get_component(self.SHIP_COMPONENT)
        ship.x += dx
        ship.y += dy
        self._in_bounds(ship)

    def _can_place(self, ship):
        placed_ships = [s for key, s in self.components.items()
                        if re.match('placed_\d', key)]
        for placed_ship in placed_ships:
            if ship.overlaps(placed_ship):
                return False
        return True

    def handle_placement_event(self, event, window):
        """Drop the ship that is being placed onto the board."""
        self._num += 1
        ship = self.get_component(self.SHIP_COMPONENT)
        self.add_component(self.SHIP_COMPONENT, None)
        self.add_component('placed_%s' % self._num, ship)

    def rotate_placement_ship(self):
        """Rotate the ship that is currently being placed."""
        ship = self.get_component(self.SHIP_COMPONENT)
        ship.rotate()
        self._in_bounds(ship)

    def has_focus(self, x, y, window):
        """The board has focus. Update put the cursor where we want it."""
        ship = self.get_component(self.SHIP_COMPONENT)
        if ship:
            window.move_cursor(ship.x, ship.y)


class ShipSelectionView(View):
    def __init__(self, x, y):
        super().__init__(x, y)
        self._table = Table(0, 0, [
            ColumnSpec('Name', 11),
            ColumnSpec('Symbol', 16)
        ])
        self._table.rows = [[k, v] for k, v in _SHIPS_HORIZ.items()]
        self.add_component('table', self._table)
        self.active_component = 'table'

    def get_selected_ship_name(self):
        name, _ = self._table.selected_row
        return name

    def delete_ship(self, ship_name_to_delete):
        new_ships = []
        for row in self._table.rows:
            ship_name = row[0]
            if ship_name != ship_name_to_delete:
                new_ships.append(row)
        self._table.rows = new_ships

    def handle_event(self, event, window):
        pass


class PlacementController(Controller):
    SHIP_VIEW_NAME = 'ships'
    BOARD_VIEW_NAME = 'board'

    def __init__(self):
        super().__init__()
        self.add_view(self.BOARD_VIEW_NAME, BoardView())
        self.add_view(self.SHIP_VIEW_NAME, ShipSelectionView(
            0, self.get_view(self.BOARD_VIEW_NAME).bottom + 1))
        self.active_view = self.SHIP_VIEW_NAME

    def render(self, window):
        super().render(window)

    def _select_ship_from_ship_list(self, ship_name):
        # First remove the ship from the list of ships.
        ship_view = self.get_view(self.SHIP_VIEW_NAME)
        ship_view.delete_ship(ship_name)

        # Set the ship in the board that is currently being placed.
        board_view = self.get_view(self.BOARD_VIEW_NAME)
        board_view.set_ship(ship_name)

        # Set the active view to the board so events are properly sent to it.
        self.active_view = self.BOARD_VIEW_NAME

    def _handle_ships_event(self, event, window):
        if event == KEY_ENTER:
            ship = self.active_view.get_selected_ship_name()
            self._select_ship_from_ship_list(ship)

    def _handle_board_event(self, event, window):
        if event in {KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN}:
            self.active_view.handle_move_event(event, window)
        elif event == KEY_ENTER:
            self.active_view.handle_placement_event(event, window)
            self.active_view = self.SHIP_VIEW_NAME
        elif event == 'r':
            self.active_view.rotate_placement_ship()

    def handle_event(self, event, window):
        getattr(self, '_handle_%s_event' % self.active_view_name)(
            event, window
        )


def main():
    loop = asyncio.get_event_loop()

    with splutter_window() as window:
        controller = PlacementController()
        loop.run_until_complete(controller.attach_to_window(window))


if __name__ == '__main__':
    main()
