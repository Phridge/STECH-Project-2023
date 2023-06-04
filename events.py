from reactivex import Subject, Observable
from reactivex.abc import DisposableBase
from reactivex.disposable import CompositeDisposable
from reactivex.subject import Subject as Event, BehaviorSubject as Var, BehaviorSubject
from reactivex.operators import combine_latest, filter, starmap
import reactivex.disposable



class Disposable:

    def dispose(self) -> None:
        for key, value in vars(self).items():
            if isinstance(value, (Disposable, DisposableBase)):
                value.dispose()


class Events(DisposableBase):
    def __init__(self, **kwargs):
        self._sub = reactivex.disposable.Disposable()
        vars(self).update(kwargs)

    def extend(self, **kwargs):
        return Events(**vars(self), **kwargs)

    def add_lever(self, lever):
        new = {}
        predicate = True
        self._sub = lever.subscribe(lambda p: locals().update(predicate=p))
        for key, value in vars(self).items():
            if isinstance(value, Observable):
                new[key] = value.pipe(
                    filter(lambda d: predicate),
                )
            else:
                new[key] = value
        return Events(**new)

    def dispose(self) -> None:
        self._sub.dispose()


Unset = object()


def OptVar(init):
    return Var(init) if init is not Unset else Event()
