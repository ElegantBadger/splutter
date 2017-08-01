import asyncio

from splutter import Controller
from splutter.text import TextField
from splutter import View
from splutter import splutter_window
from splutter import Border


class InputView(View):
    def __init__(self, width, height):
        super().__init__()
        self._input = TextField(1, 1, width=width, max_length=140, text='')
        self._border = Border(0, 0, width + 2, 2)
        self.add_component('input', self._input)
        self.add_component('border', self._border)
        self.active_component = 'input'
        self.size_to_components()


class ChatController(Controller):
    TEXT_INPUT_NAME = 'text'

    def __init__(self):
        super().__init__()
        self.add_view(self.TEXT_INPUT_NAME, InputView(12, 2))
        self.active_view = self.TEXT_INPUT_NAME

    def handle_event(self, event, window):
        pass


def main():
    loop = asyncio.get_event_loop()

    with splutter_window() as window:
        controller = ChatController()
        loop.run_until_complete(controller.attach_to_window(window))


if __name__ == '__main__':
    main()
