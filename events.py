from reactivex.abc import DisposableBase
from reactivex.subject import Subject as Event, BehaviorSubject as Var


class Events:
    def __init__(self, **kwargs):
        vars(self).update(kwargs)

    def override(self, **kwargs):
        return Events(**vars(self), **kwargs)


class Disposable:
    def dispose(self) -> None:
        for value in vars(self).values():
            if hasattr(value, "dispose"):
                value.dispose()