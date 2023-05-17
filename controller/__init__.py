from reactivex.disposable import CompositeDisposable

from events import Disposable, Var, Event


class Controller(Disposable):

    def __init__(self):
        self._subs = CompositeDisposable()

    def set_enabled(self):
        pass


class Screen(Controller):

    def __init__(self):
        super().__init__()
        self.change_controller = Event()
        self.event = Event()  # separates Subject für eventuelle Events die in diesem Screen stattfinden
        self.game_command = Event()

    def push_screen(self, screen):
        from main_controller import PushScreen
        self.game_command.on_next(PushScreen(screen))

    def go_to(self, screen):
        from main_controller import SwitchScreen
        self.game_command.on_next(SwitchScreen(screen))

    def go_back(self):
        from main_controller import PopScreen
        self.game_command.on_next(PopScreen())

    @classmethod
    def init_fn(cls, *args, **kwargs):
        return lambda e: cls(e, *args, **kwargs)

    def get_view(self):
        raise NotImplementedError