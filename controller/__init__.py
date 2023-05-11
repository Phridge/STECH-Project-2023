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


    def get_view(self):
        raise NotImplementedError