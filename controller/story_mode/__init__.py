from pyglet.graphics import Group
from reactivex.abc import DisposableBase
from reactivex.disposable import SerialDisposable
from reactivex.operators import scan, take_while, map as rmap

from controller import Screen


class Machine(DisposableBase):
    """
    Stellt den Ablauf des Levels in einer Finite State Machine dar.
    Hat mehrere Schritte, die nacheinander abgearbeitet werden (durch machine.next()).
    """

    def __init__(self, stuff):
        self.stuff = stuff
        self.index = -1
        self.disposable = SerialDisposable()
        self.next()

    def next(self):
        """
        Die Maschine in den nächsten Zustand bringen

        Die Ressourcen vom vorherigen Schritt, falls existierend, werden gelöscht, und die
        Funktion des nächsten Zustands wird ausgeführt.
        """
        self.index += 1
        if self.index >= len(self.stuff):
            return
        self.disposable.disposable = self.stuff[self.index]()

    def dispose(self):
        self.disposable.dispose()


class Level(Screen):
    def __init__(self):
        super().__init__()


        # dient, um Objekte manuell nach vorne und hinten zu schieben. Je weniger er genutzt wird, umso performanter ist alles.
        # Standardmäßig ist alles im Mittelgrund zwischen Vorder- und Hintergrund
        self.background = Group(0)
        self.foreground = Group(1)
        self.overlay = Group(2)


def linear(t):
    return t


def animate(lo, hi, time, update_event, map=lambda x: x, interp=linear):
    """
    Animiert einen Wert von lo nach hi über gegebene Zeit.
    :param lo: startwert.
    :param hi: endwert.
    :param time: zeitspanne der animation.
    :param update_event: observable, welches das "timing" vorgibt (z.B. events.update)
    :param map: optionale mapping-funktion, die den Animierten wert in etwas anderes konvertiert.
    :param interp: Interpolierungsfunktion. zur verfügung steht aktuell "linear", welches gleichmäßig vom einen zum anderen wert animiert.
    :return: Ein Observable, welches schrittweise den animierten wert liefert
    """
    animation = update_event.pipe(
        scan(float.__add__, 0.0),
        take_while(lambda t: t <= time, inclusive=True),
        rmap(lambda t: lo + (hi - lo) * interp(min(t, time) / time)),
        rmap(map)
    )
    return animation
