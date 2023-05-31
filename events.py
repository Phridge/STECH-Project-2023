from reactivex import Subject
from reactivex.abc import DisposableBase
from reactivex.subject import Subject as Event, BehaviorSubject as Var, BehaviorSubject


class Events:
    def __init__(self, **kwargs):
        vars(self).update(kwargs)

    def extend(self, **kwargs):
        return Events(**vars(self), **kwargs)


class Disposable:
    def dispose(self) -> None:
        for value in vars(self).values():
            if isinstance(value, (Disposable, DisposableBase)):
                value.dispose()


Unset = object()


def OptVar(init):
    return Var(init) if init is not Unset else Event()
