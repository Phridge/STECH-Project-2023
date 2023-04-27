"""
Hier sind die ObjectsClasses und Funktionen enthalten für die Analyse und auswertung des Spieles

To do:
→ Mit Richard drüber gucken, ob dass Sinn machen kann
→ In die MAin File anbinden via CollectionClass Variable, den Window Events für die User eingabe,
    als auch der übergabe des Aktuell zu schreibenden Chars (generiert aus dem Programm)

"""


# Klasse welche für die Datensammlung da ist.
# Der zu trackende Zeichensatz ist quasi latin-1 also Deutsch. Mögliche ergänzung kann folgen...
class CharCollection:
    def __Collection__(self, level, startTime, playDate):
        self.charList = [
            ['0', 0, 0], ['1', 0, 0], ['2', 0, 0], ['3', 0, 0], ['4', 0, 0], ['5', 0, 0],
            ['6', 0, 0], ['7', 0, 0], ['8', 0, 0], ['9', 0, 0], ['a', 0, 0], ['b', 0, 0],
            ['c', 0, 0], ['d', 0, 0], ['e', 0, 0], ['f', 0, 0], ['g', 0, 0], ['h', 0, 0],
            ['i', 0, 0], ['j', 0, 0], ['k', 0, 0], ['l', 0, 0], ['m', 0, 0], ['n', 0, 0],
            ['o', 0, 0], ['p', 0, 0], ['q', 0, 0], ['r', 0, 0], ['s', 0, 0], ['t', 0, 0],
            ['u', 0, 0], ['v', 0, 0], ['w', 0, 0], ['x', 0, 0], ['y', 0, 0], ['z', 0, 0],
            ['A', 0, 0], ['B', 0, 0], ['C', 0, 0], ['D', 0, 0], ['E', 0, 0], ['F', 0, 0],
            ['G', 0, 0], ['H', 0, 0], ['I', 0, 0], ['J', 0, 0], ['K', 0, 0], ['L', 0, 0],
            ['M', 0, 0], ['N', 0, 0], ['O', 0, 0], ['P', 0, 0], ['Q', 0, 0], ['R', 0, 0],
            ['S', 0, 0], ['T', 0, 0], ['U', 0, 0], ['V', 0, 0], ['W', 0, 0], ['X', 0, 0],
            ['Y', 0, 0], ['Z', 0, 0], ['ä', 0, 0], ['ö', 0, 0], ['ü', 0, 0], ['Ä', 0, 0],
            ['Ö', 0, 0], ['Ü', 0, 0], ['!', 0, 0], ['"', 0, 0], ['§', 0, 0], ['%', 0, 0],
            ['&', 0, 0], ['/', 0, 0], ['(', 0, 0], [')', 0, 0], ['=', 0, 0], ['ß', 0, 0],
            ['?', 0, 0], ['`', 0, 0], ['´', 0, 0], ['+', 0, 0], ['*', 0, 0], ['~', 0, 0],
            ['#', 0, 0], ['\'', 0, 0], ['-', 0, 0], ['_', 0, 0], ['.', 0, 0], [':', 0, 0],
            [',', 0, 0], [';', 0, 0], ['<', 0, 0], ['>', 0, 0], ['|', 0, 0], ['^', 0, 0],
            ['°', 0, 0], ['²', 0, 0], ['³', 0, 0], ['€', 0, 0], ['@', 0, 0], ['{', 0, 0],
            ['[', 0, 0], [']', 0, 0], ['}', 0, 0], ['\\', 0, 0]
        ]
        self.level = level
        self.startTime = startTime
        self.endTime = 0
        self.playDate = playDate


# initiiert das Sammeln der Daten, indem das Level, die Zeit wann es beginnt und das aktuelle Datum übergeben werden
def startTracking(currentLevel, startTime, currentDate):
    CollectingClass = CharCollection(currentLevel, startTime, currentDate)

    return CollectingClass


# setzt die Endzeit in die Klasse ein, wenn das Level beendet wurde
def endTracking(CollectorClass, finishTime):
    CollectorClass.endTime = finishTime


# Prüft UserInputs mit den zu erwartenden Chars und macht abhängig davon einen Eintrag im Analyseobjekt
def inputCompare(Collectionclass, CurrentChar, UserInputChar):
    # Ist der InputChar, dass was erwartet wird, zähle den count des Buchstaben hoch
    if CurrentChar == UserInputChar:
        for ArrayLength in Collectionclass.charList:
            if Collectionclass.charList[ArrayLength][0] == CurrentChar:
                Collectionclass.charList[ArrayLength][1] = Collectionclass.charList[ArrayLength][1] + 1
    else:  # Zähle zusätzlich noch die Fehlervariable hoch
        for ArrayLength in Collectionclass.charList:
            if Collectionclass.charList[ArrayLength][0] == CurrentChar:
                Collectionclass.charList[ArrayLength][1] = Collectionclass.charList[ArrayLength][1] + 1
                Collectionclass.charList[ArrayLength][1] = Collectionclass.charList[ArrayLength][2] + 1
