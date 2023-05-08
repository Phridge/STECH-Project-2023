import json
from database import new_session, Save
from sqlalchemy import update, select
import input_tracker

"""
Funktion, die die Usersettings speichert und local in einer Datei speichert. 
Gespeicherte Parameter:
--> Ausgewählte RGB Farbe
--> Sound Volume
--> Fenstergröße 
--> Ist das Spei lFenster auf Vollbild (boolean)

Warum JSON File? Ich fande diese Idee in sicht auf "persisted settings" sinnvoll
"""


def save_to_json_file(red, blue, green, volume, windowsize, screenfull):
    with open('settings.json', 'w', encoding='utf-8') as f:
        json.dump([red, green, blue, volume, windowsize, screenfull], f, ensure_ascii=False, indent=5)


# Setzt alle game Saves auf ein Preset, sollten keine Parameter übergeben werden
# aktualisiert die Settings des Game Saves, in dem man Werte übergibt
def assign_game_saves(game_save_nr, language, keyboard_layout, level_progress):
    if game_save_nr & language & keyboard_layout & level_progress is None:
        for x in range(2):
            with new_session() as session:
                s = Save(
                    id=x + 1,
                    level_progress=None,
                    language="German",
                    keyboard_layout="QERTZ",
                )
                session.add(s)
                session.commit()
            x += 1
    else:
        with new_session() as session:

            if level_progress is None:
                level_progress = select(Save.level_progress).where(Save.id == game_save_nr)
            if language is None:
                language = select(Save.language).where(Save.id == game_save_nr)
            if keyboard_layout is None:
                keyboard_layout = select(Save.keyboard_layout).where(Save.id == game_save_nr)

            session.execute(update(Save).
                            where(Save.id == game_save_nr).
                            values(
                                level_progress=level_progress,
                                language=language,
                                keyboard_layout=keyboard_layout
                            ))
            session.commit()


# ------------Under Construction------------
"""def save_game(game_save_nr, language, keyboard_layout, level_progress):
    with new_session()as session:
    s = Table(
      Column_name=Wert,
    )

    session.add(s)
    session.commit()

    result = session.execute(select(Table))

    print(select(Table).where(Table.Column_name == Vergleichsparameter))
    print(result.all())

    session.execute(delete(Table))
    session.commit()

pass#Das hier nötig?"""
