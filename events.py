from reactivex import Subject, Observable
from reactivex.abc import DisposableBase, ObserverBase, SchedulerBase
from reactivex.disposable import CompositeDisposable
from reactivex.subject import Subject as Event, BehaviorSubject as Var, BehaviorSubject
from reactivex.operators import combine_latest, filter, starmap
import reactivex.disposable



class Disposable:

    def dispose(self) -> None:
        for key, value in vars(self).items():
            if isinstance(value, (Disposable, DisposableBase)):
                value.dispose()


def valved(valve, initial=False):
    def valved_(observable):
        def on_subscribe(subscriber: ObserverBase, scheduler: SchedulerBase | None = None) -> DisposableBase | None:
            valve_state = initial

            def on_base_next(x):
                if valve_state:
                    subscriber.on_next(x)

            def on_valve_next(state):
                nonlocal valve_state
                valve_state = state

            return CompositeDisposable(
                valve.subscribe(on_valve_next, subscriber.on_error, subscriber.on_completed),
                observable.subscribe(on_base_next, subscriber.on_error, subscriber.on_completed)
            )

        return Observable(on_subscribe)

    return valved_



class Events:
    def __init__(self, **kwargs):
        vars(self).update(kwargs)

    def extend(self, **kwargs):
        return Events(**vars(self), **kwargs)

    def add_valve(self, valve):
        new = {}
        for key, value in vars(self).items():
            if isinstance(value, Observable):
                new[key] = value.pipe(valved(valve))
            else:
                new[key] = value
        return Events(**new)



Unset = object()


def OptVar(init):
    return Var(init) if init is not Unset else Event()
