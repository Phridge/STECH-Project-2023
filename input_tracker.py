"""
Hier sind die ObjectsClasses und Funktionen enthalten für die Analyse und auswertung des Spieles

To do:
→ In die Main File anbinden via CollectionClass Variable, den Window Events für die User eingabe,
    als auch der übergabe des Aktuell zu schreibenden Chars (generiert aus dem Programm)


→ Info: Habe der Texttracker Klasse mal "getter" Funktionen gegeben, damit man die Datensätze in die Analyse klasse
        später geben kann und dadurch alle daten zentral hat zum späteren abspeichern

→ Für die CharList siehe: https://www.w3schools.com/python/python_lists_comprehension.asp
    |--> Liste der möglichen Buchstaben hardcoden
"""
import datetime
import time
from collections import namedtuple
from dataclasses import dataclass



class InputAnalysis:
    """
    Klasse welche für die Datensammlung da ist.
    Der zu trackende Zeichensatz ist quasi latin-1 also Deutsch. Mögliche ergänzung kann folgen...
    Array besteht aus:
    [<Zeichen>, <Anzahl wie oft es vorkam>, <Anzahl wie oft anderes Zeichen gedrückt wurde>, <average Time needed>]
    """
    def __init__(self):
        self.char_list = [
            ['0', 0, 0, 0], ['1', 0, 0, 0], ['2', 0, 0, 0], ['3', 0, 0, 0], ['4', 0, 0, 0], ['5', 0, 0, 0],
            ['6', 0, 0, 0], ['7', 0, 0, 0], ['8', 0, 0, 0], ['9', 0, 0, 0], ['a', 0, 0, 0], ['b', 0, 0, 0],
            ['c', 0, 0, 0], ['d', 0, 0, 0], ['e', 0, 0, 0], ['f', 0, 0, 0], ['g', 0, 0, 0], ['h', 0, 0, 0],
            ['i', 0, 0, 0], ['j', 0, 0, 0], ['k', 0, 0, 0], ['l', 0, 0, 0], ['m', 0, 0, 0], ['n', 0, 0, 0],
            ['o', 0, 0, 0], ['p', 0, 0, 0], ['q', 0, 0, 0], ['r', 0, 0, 0], ['s', 0, 0, 0], ['t', 0, 0, 0],
            ['u', 0, 0, 0], ['v', 0, 0, 0], ['w', 0, 0, 0], ['x', 0, 0, 0], ['y', 0, 0, 0], ['z', 0, 0, 0],
            ['A', 0, 0, 0], ['B', 0, 0, 0], ['C', 0, 0, 0], ['D', 0, 0, 0], ['E', 0, 0, 0], ['F', 0, 0, 0],
            ['G', 0, 0, 0], ['H', 0, 0, 0], ['I', 0, 0, 0], ['J', 0, 0, 0], ['K', 0, 0, 0], ['L', 0, 0, 0],
            ['M', 0, 0, 0], ['N', 0, 0, 0], ['O', 0, 0, 0], ['P', 0, 0, 0], ['Q', 0, 0, 0], ['R', 0, 0, 0],
            ['S', 0, 0, 0], ['T', 0, 0, 0], ['U', 0, 0, 0], ['V', 0, 0, 0], ['W', 0, 0, 0], ['X', 0, 0, 0],
            ['Y', 0, 0, 0], ['Z', 0, 0, 0], ['ä', 0, 0, 0], ['ö', 0, 0, 0], ['ü', 0, 0, 0], ['Ä', 0, 0, 0],
            ['Ö', 0, 0, 0], ['Ü', 0, 0, 0], ['!', 0, 0, 0], ['"', 0, 0, 0], ['§', 0, 0, 0], ['%', 0, 0, 0],
            ['&', 0, 0, 0], ['/', 0, 0, 0], ['(', 0, 0, 0], [')', 0, 0, 0], ['=', 0, 0, 0], ['ß', 0, 0, 0],
            ['?', 0, 0, 0], ['`', 0, 0, 0], ['´', 0, 0, 0], ['+', 0, 0, 0], ['*', 0, 0, 0], ['~', 0, 0, 0],
            ['#', 0, 0, 0], ['-', 0, 0, 0], ['_', 0, 0, 0], ['.', 0, 0, 0], [':', 0, 0, 0], [' ', 0, 0, 0],
            [',', 0, 0, 0], [';', 0, 0, 0], ['<', 0, 0, 0], ['>', 0, 0, 0], ['|', 0, 0, 0], ['^', 0, 0, 0],
            ['°', 0, 0, 0], ['²', 0, 0, 0], ['³', 0, 0, 0], ['€', 0, 0, 0], ['@', 0, 0, 0], ['{', 0, 0, 0],
            ['[', 0, 0, 0], [']', 0, 0, 0], ['}', 0, 0, 0], ['\\', 0, 0, 0], ['\'', 0, 0, 0]
        ]
        self.char_count = 0
        self.correct_char_count = 0
        self.text = ""
        self.text_written = ""
        self.time = 0.0
        self.correct_time = 0.0

    def track_input(self, char, is_correct, time_taken: datetime.timedelta):
        """
        Buchstaben tracken.
        :param char: Der eingegebene Buchstabe
        :param is_correct: War das der richtige Buchstabe? Bool.
        :param time_taken: Gebrauchte zeit.
        """
        self.char_count += 1
        self.time += time_taken.total_seconds()
        self.text_written += char

        if is_correct:
            self.correct_char_count += 1
            self.correct_time += time_taken.total_seconds()
            self.text += char

        for entry in self.char_list:
            if entry[0] == char:
                entry[1] += 1
                if not is_correct:
                    entry[2] += 1
                entry[3] += time_taken.total_seconds()
                break

    @property
    def accuracy(self):
        return self.correct_char_count / self.char_count

    @property
    def real_type_speed(self):
        return self.correct_char_count / self.time

    @property
    def logical_type_speed(self):
        return self.correct_time / self.correct_char_count

# Klasse, welche den aktuellen Text beinhaltet und die derzeitige Position im Text wiedergibt
class TextTracker:
    """
    Eingabetracker. Gibt an, welcher Text zu schreiben ist, bis wohin bisher geschrieben wurde und ob die letzte eingabe
    richtig war. Nimmt optional einen Inputtracker an. Um mit diesen über eingabedauer zu reden, wird die letzte eingabezeit
    gespeichert.
    Der erste Buchstabe wird zeitlich nicht gemessen, da keine Referenzzeit existiert.
    """

    def __init__(self, current_text, input_analysis=None):
        self.current_text = current_text
        self.written_text = ''
        self.time_per_char = [0]
        self.string_finished = False
        self.write_time_start = None
        self.write_time_end = None
        self.last_input_correct = True
        self.last_input = None
        self.input_analysis = input_analysis or InputAnalysis()

    @property
    def current_position(self):
        return len(self.written_text)

    @property
    def is_finished(self):
        return self.text_valid and len(self.written_text) >= len(self.current_text)

    @property
    def text_valid(self):
        return len(self.current_text) > 0

    def start_timer(self):
        self.input_analysis.start_timer()
        self.last_input = datetime.datetime.now()

    def accept_char(self, char):
        """
        Akzeptiert eine Eingabe des Nutzers.
        :param char: der Buchstabe, der gedrückt wurde
        """
        # nix machen wenn schon fertig
        if self.is_finished or not self.text_valid:
            return

        # zeit messen
        current_time = datetime.datetime.now()
        time_taken = current_time - self.last_input if self.last_input else None  # keine zeitangabe wenn nicht gestartet vorher

        # buchstabe richtig?
        is_correct = char == self.current_text[self.current_position]

        # wenn richtig, dann fortschritt
        if is_correct:
            self.written_text += char

        self.last_input_correct = is_correct

        # wenn zeitmessungen da sind, werden diese an den InputAnanysis-Instanz gesendet
        if time_taken:
            self.input_analysis.track_input(char, is_correct, time_taken)

        self.last_input = current_time


# Funktion, welche die Zeit in Millisekunden Ausgibt
def current_milli_time():
    return round(time.time() * 1000)
