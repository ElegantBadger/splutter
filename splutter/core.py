import asyncio

from splutter.window import EventBus
from splutter.exceptions import CloseSplutterWindow


class Component(object):
    BIND_TOP_LEFT = 1
    BIND_MIDDLE = 2

    def __init__(self, x, y, bind_to=BIND_TOP_LEFT):
        self._x = x
        self._y = y
        self._width = 0
        self._height = 0
        self._bind_to = bind_to

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, new_x):
        self._x = new_x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, new_y):
        self._y = new_y

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def bottom(self):
        return self._y + self.height

    @property
    def right(self):
        return self._x + self.width

    def overlaps(self, other):
        """Check if this component and the other one overlap."""
        pass

    def _render(self, x, y, window):
        raise NotImplementedError('_render')

    def render(self, zero_x, zero_y, window):
        if self._bind_to == self.BIND_TOP_LEFT:
            self._render(zero_x + self.x, zero_y + self.y, window)
        elif self._bind_to == self.BIND_MIDDLE:
            x = self.x - self.width // 2
            y = self.y - self.height // 2
            self._render(zero_x + x, zero_y + y, window)

    def move(self, x=None, y=None):
        self._x = x if x is not None else self._x
        self._y = y if y is not None else self._y


class View(Component):
    def __init__(self, x=0, y=0, bind_to=Component.BIND_TOP_LEFT):
        super().__init__(x, y, bind_to=bind_to)
        self._components = {}
        self._active_component = None

    @property
    def active_component(self):
        return self._components.get(self._active_component)

    @active_component.setter
    def active_component(self, new_active_component):
        self._active_component = new_active_component

    def get_active_component_stack(self, stack):
        if isinstance(self.active_component, View):
            stack.append(self)
            stack.extend(self.active_component.get_active_component_stack)
        else:
            stack.append(self)
            stack.append(self.active_component)
        return stack

    def size_to_components(self):
        self._width = 0
        self._height = 0
        for component in self._components.values():
            if component:
                self._width = max(self._width, component.right)
                self._height = max(self._height, component.bottom)

    def add_component(self, name, component):
        self._components[name] = component

    def remove_component(self, name):
        if name in self._components:
            del self._components[name]

    def get_component(self, name):
        return self._components[name]

    @property
    def components(self):
        return self._components

    def render(self, window):
        for component in self._components.values():
            if component:
                component.render(self._x, self._y, window)

    def has_focus(self, x, y, window):
        if self.active_component is not None:
            self.active_component.has_focus(self.x + x, self.y + y, window)

    def handle_event(self, event, window):
        """Handle a key press inside a splutter window.

        This should be overridden by a subclass. It passes by default so that
        the event bus can safely call it.

        :type key_code: :class:`splutter.window.WindowEvent`
        :param key_code: The event that was triggered in the window.

        :type window: :class:`splutter.window.Window`
        :param window: The window this event was detected in.
        """
        pass


class Controller(object):
    def __init__(self, bus=None):
        self._views = {}
        if bus is None:
            bus = EventBus(self)
        self._event_bus = bus
        self._active_view = None

    @property
    def active_view(self):
        return self._views.get(self._active_view)

    @active_view.setter
    def active_view(self, new_active_view):
        self._active_view = new_active_view

    @property
    def active_view_name(self):
        return self._active_view

    def add_view(self, name, view):
        self._views[name] = view
        if self._active_view is None:
            self._active_view = view

    def get_view(self, name):
        return self._views.get(name)

    def render(self, window):
        for _, view in self._views.items():
            view.render(window)
        if self.active_view is not None:
            self.active_view.has_focus(0, 0, window)

    def _propagate_event(self, event, window):
        """Propagate an event down to the base level view.

        An event first trickles down to the bottom level view, and then
        bubbles back up the view stack.
        """
        if self.active_view is None:
            return
        self._event_bus.propagate_event(event, self.active_view, window)

    def handle_event(self, event, window):
        """Handle a key press inside a splutter window.

        This should be overridden by a subclass

        :type key_code: :class:`splutter.window.WindowEvent`
        :param key_code: The event that was triggered in the window.

        :type window: :class:`splutter.window.Window`
        :param window: The window this event was detected in.
        """
        raise NotImplementedError('handle_key')

    async def attach_to_window(self, window):
        """Attach this controller to a window.

        Once a controller is attached to a window it will block. Events in the
        window will trigger :meth:`splutter.core.Controller.handle_key`. To
        close the window raise a
        :class:`splutter.exceptions.CloseSplutterWindow` exception.

        :type window: :class:`splutter.window.Window`
        :param window: The window class to attach this controller to.
        """
        try:
            while True:
                self._poll(window)
                window.erase()
                self.render(window)
                window.update_cursor()
                window.refresh()
                await asyncio.sleep(0)
        except KeyboardInterrupt:
            window.close_reason = 'Ctrl-C'
        except CloseSplutterWindow as e:
            window.close_reason = str(e)

    def _poll(self, window):
        event = window.get_event()
        if event is not None:
            self._propagate_event(event, window)
