from reactivex import Subject, Observable
from reactivex.abc import DisposableBase
from reactivex.disposable import CompositeDisposable
from reactivex.subject import Subject as Event, BehaviorSubject as Var, BehaviorSubject
from reactivex.operators import combine_latest, filter, starmap



class Disposable:
    _is_disposed = False

    def dispose(self) -> None:
        if self._is_disposed:
            return

        for key, value in vars(self).items():
            if isinstance(value, (Disposable, DisposableBase)):
                value.dispose()
                setattr(self, key, None)

        self._is_disposed = True

#    def __del__(self):
#        if not self._is_disposed:
#            self.dispose()


class Events:
    def __init__(self, **kwargs):
        vars(self).update(kwargs)

    def extend(self, **kwargs):
        return Events(**vars(self), **kwargs)

    def add_lever(self, lever):
        new = {}
        for key, value in vars(self).items():
            if isinstance(value, Observable):
                new[key] = value.pipe(
                    combine_latest(lever),
                    filter(lambda d: d[1]),
                    starmap(lambda v, p: v),
                )
            else:
                new[key] = value
        return Events(**new)


Unset = object()


def OptVar(init):
    return Var(init) if init is not Unset else Event()
