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


# Klasse welche für die Datensammlung da ist.
# Der zu trackende Zeichensatz ist quasi latin-1 also Deutsch. Mögliche ergänzung kann folgen...
# Array besteht aus:
# [<Zeichen>, <Anzahl wie oft es vorkam>, <Anzahl wie oft anderes Zeichen gedrückt wurde>, <average Time needed>]
class InputAnalysis:
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
        self.chars_typed = 0
        self.chars_typed_correctly = 0
        self.acc_time = 0.0

    def track_input(self, char, is_correct, time_taken: datetime.timedelta):
        self.chars_typed += 1
        self.acc_time += time_taken.total_seconds()

        if is_correct:
            self.chars_typed_correctly += 1

        for entry in self.char_list:
            if entry[0] == char:
                entry[1] += 1
                if not is_correct:
                    entry[2] += 1
                entry[3] += time_taken.total_seconds()
                break

    def set_level_text(self, level_text):
        self.level_text = level_text

    def set_written_text_by_user(self, user_text):
        self.written_text_by_user = user_text

    def set_time_per_char(self, time_per_char):
        self.time_per_char = time_per_char

    # setzt die Endzeit in die Klasse ein, wenn das Level beendet wurde
    def ind_tracking(self, finish_time):
        self.end_time = finish_time

    # Prüft UserInputs mit den zu erwartenden Chars und macht abhängig davon einen Eintrag im Analyseobjekt
    def input_compare(self, current_char, user_input_char):
        is_correct = False
        # Ist der InputChar, dass was erwartet wird, zähle den count des Buchstaben hoch
        if current_char == user_input_char:
            for item in self.char_list:
                if item[0] == user_input_char:
                    item[1] += 1
                    is_correct = True
        else:  # Zähle zusätzlich noch die Fehlervariable hoch
            for item in self.char_list:
                if item[0] == user_input_char:
                    item[1] += 1
                    item[2] += 1

        return is_correct

    """Mögliche Verbesserung Median stat arithmetisches Mittel für Durchschnitt"""
    # Funktion, welche den vom User geschriebenen Text durchgeht und ein durchschnittswert der dafür gebrauchten zeiten
    # aus self.time_per_char ermittelt
    def tag_average_time_per_Char(self):
        # Durchlauf Variable um Position der zum Buchstaben zugehörigen Zeit im Array self.time_per_char zu ermitteln
        i = 0
        # Zähl variable, um Teiler für Durchschnittswert zu ermitteln
        j = 0
        for char_data in self.char_list:
            for x in self.written_text_by_user:
                # Wenn der Buchstabe x gleich dem des Eintrages in der self.char_list ist
                if char_data[0] == x:
                    # Addiere die Zeit auf die schon bestehende Zeit auf
                    char_data[3] += self.time_per_char[i]
                    j += 1
                i += 1
            # Zeile den Aufsummierten wert des Buchstaben in der self.char_list durch die Anzahl der Aufsummierungen
            char_data[3] = char_data / j

# Klasse, welche den aktuellen Text beinhaltet und die derzeitige Position im Text wiedergibt
class TextTracker:

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
        return len(self.current_text) > 0 and len(self.written_text) >= len(self.current_text)

    def start_timer(self):
        self.input_analysis.start_timer()
        self.last_input = datetime.datetime.now()

    def accept_char(self, char):
        """
        Akzeptiert eine Eingabe des Nutzers.
        ACHTUNG: start_timer davor starten!
        :param char: der Buchstabe, der gedrückt wurde
        :return:
        """
        # nix machen wenn schon fertig
        if self.is_finished:
            return

        # zeit messen
        current_time = datetime.datetime.now()
        time_taken = current_time - self.last_input if self.last_input else None  # keine zeitangabe wenn nicht gestartet vorher

        is_correct = char == self.current_text[self.current_position]

        if is_correct:
            self.written_text += char

        self.last_input_correct = is_correct

        if time_taken:
            self.input_analysis.track_input(char, is_correct, time_taken)

        self.last_input = current_time

    def reset(self):
        self.written_text = ""
        self.last_input_correct = True

    # fügt den geschriebenen Buchstaben zum text hinzu, welcher vom Benutzer geschrieben wurde
    def update_written_text(self, user_input):
        self.write_time_end = current_milli_time()
        self.written_text = self.written_text + user_input

    # Schreibt die Zeit, die für den aktuellen Buchstaben benötigt wurde in ein Array
    def input_time(self):
        time_needed = self.write_time_end - self.write_time_start

        if self.current_position == 0:
            self.time_per_char[0] = time_needed
        else:
            self.time_per_char.append(time_needed)

    def get_written_text(self):
        return self.written_text

    def get_current_text(self):
        return self.current_text

    def get_time_per_char(self):
        return self.time_per_char


# Funktion, welche die Zeit in Millisekunden Ausgibt
def current_milli_time():
    return round(time.time() * 1000)
