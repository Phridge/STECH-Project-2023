import json
import pickle
from datetime import timedelta

from sqlalchemy.exc import NoResultFound

import color_scheme
from database import new_session, Save, Run, Char, Level
from sqlalchemy import update, select, func, delete
from sqlalchemy.sql import text
from input_tracker import TextTracker, InputAnalysis

"""
Funktion, die die Usersettings speichert und local in einer Datei speichert. 
Gespeicherte Parameter:
--> Ausgewählte RGB Farbe
--> Sound Volume
--> Fenstergröße 
--> Ist das Spei lFenster auf Vollbild (boolean)

Warum JSON File? Ich fande diese Idee in sicht auf "persisted settings" sinnvoll


Noch zu machen:
--> Tests auf Funktionsweise!!!

"""

# Setzt alle game Saves auf ein Preset, sollten keine Parameter übergeben werden
# aktualisiert die Settings des Game Saves, in dem man Werte übergibt

def save_text_tracker(game_save_nr: int, level_name: str, text_tracker: TextTracker):
    """
    TODO
    :param game_save_nr: Nummer des Speicherstands
    :param level_name: Bezeichnung des jeweiligen Levels
    :param text_tracker: TODO
    """
    with new_session() as session:
        try:
            level = session.execute(select(Level).where(Level.name == level_name)).scalar_one()
        except NoResultFound:
            level = Level(
                name=level_name,
            )
            session.add(level)
            session.commit()
            session.refresh(level)

        run = Run(
            save_id=game_save_nr,
            level_id=level.id,
            preset_text=text_tracker.input_analysis.text,
            typed_text=text_tracker.input_analysis.text_written,
            char_count=text_tracker.input_analysis.char_count,
            time=text_tracker.input_analysis.time,
            correct_char_count=text_tracker.input_analysis.correct_char_count,
            correct_time=text_tracker.input_analysis.correct_time,
        )
        session.add(run)
        session.commit()
        session.refresh(run)

        for key, count, wrong, time in text_tracker.input_analysis.char_list:
            if count == 0:
                continue
            session.add(Char(
                run_id=run.id,
                char=key,
                preset_char_count=count,
                typed_char_count=count - wrong,
                avg_time_per_char=time / count,
                accuracy=(count - wrong) / count,
            ))
        session.commit()


def save_run(game_save_nr: int, level_name: str, input_analysis: InputAnalysis):
    """
    Speichert entweder 1 abgeschlossenes Level, bzw. 1 Abschnitt in Sandbox- und Lernmodus
    :param game_save_nr: Nummer des Speicherstands
    :param level_name: Bezeichnung des jeweiligen Levels
    :param input_analysis: InputAnalysis-Objekt mit berechneten Werten
    """
    with new_session() as session:
        try:
            level = session.execute(select(Level).where(Level.name == level_name)).scalar_one()
        except NoResultFound:
            level = Level(
                name=level_name,
            )
            session.add(level)
            session.commit()
            session.refresh(level)

        run = Run(
            save_id=game_save_nr,
            level_id=level.id,
            preset_text=input_analysis.text,
            typed_text=input_analysis.text_written,
            char_count=input_analysis.char_count,
            time=input_analysis.time,
            correct_char_count=input_analysis.correct_char_count,
            correct_time=input_analysis.correct_time,
        )
        session.add(run)
        session.commit()
        session.refresh(run)

        for key, count, wrong, time in input_analysis.char_list:
            if count == 0:
                continue
            session.add(Char(
                run_id=run.id,
                char=key,
                preset_char_count=count,
                typed_char_count=count - wrong,
                avg_time_per_char=time / count,
                accuracy=(count - wrong) / count,
            ))
        session.commit()


# -----------------Noch testen---------------------
def save_settings_to_db(save, fullscreen, volume, preview_color_scheme, new_screen_size):
    """
    Speichert die Save-spezifischen Einstellungen in die Datenbank. Erstellt ein neues Tupel, falls keins existiert.

    :param save: Spielstand, dem die Einstellungen angehören
    :param fullscreen: Bool, ob Fullscreen an oder aus ist
    :param volume: Lautstärke als Wert zwischen 0 und 100
    :param preview_color_scheme: Farbschema des Saves als EditableColorSchemee-Objekt
    :param new_screen_size: Bildschirmgröße als Tupel (w,h)
    """
    with new_session() as session:
        settings_pickle = pickle.dumps((fullscreen, volume, preview_color_scheme, new_screen_size))
        print((fullscreen, volume, preview_color_scheme, new_screen_size))
        try:
            save_line = session.execute(select(Save).where(Save.id == save)).scalar_one()
        except NoResultFound:
            s = Save(
                id=save,
                level_progress=0,
                settings=settings_pickle
            )
            session.add(s)
            session.commit()
        else:
            setattr(save_line, "settings", settings_pickle)
            session.commit()
            #  der Save existiert


def set_level_progress(save, level):
    """
    Speichert, wenn ein Level zum ersten Mal abgeschlossen wurde
    :param save:
    :param level:
    :return:
    """
    with new_session() as session:
        try:
            save_line = session.execute(select(Save).where(Save.id == save)).scalar_one()
        except NoResultFound:
            s = Save(
                id=save,
                level_progress=level,
                settings=pickle.dumps((False, 0, color_scheme.BlackWhite, (600, 600)))
            )
            session.add(s)
            session.commit()
        else:
            if getattr(save_line, "level_progress") < level:
                setattr(save_line, "level_progress", level)
                session.commit()


def delete_save(save):
    """
    Löscht einen Speicherstand aus der lokalen Datenbank
    :param save: zu löschender Speicherstand
    """
    with new_session() as session:
        session.execute(delete(Save).where(Save.id == save))
        session.commit()

def get_settings(save):
    """
    Holt die Settings aus der Datenbankund entschlüsselt sie
    :param save: Spielstand
    :return: Einstellungs-Objekt
    """

    with new_session() as session:
        try:
            save_line = session.execute(select(Save).where(Save.id == save)).scalar_one()
        except NoResultFound:
            return False, 0, color_scheme.BlackWhite, None
        else:
            settings_data = pickle.loads(getattr(save_line, "settings"))
            return settings_data


def get_story_progress(save):
    """
    TODO
    :param save: Spielstand
    :return: Fortschritt des Spielstands (wenn vorhanden)
    """
    with new_session() as session:
        try:
            save_line = session.execute(select(Save).where(Save.id == save)).scalar_one()
        except NoResultFound:
            return 0
        else:
            progress_data = getattr(save_line, "level_progress")
            return progress_data


# Nicht wirklich sicher, ob das geht, da das MySQL statt SQL code ist
def get_last_run_id(game_save):
    output_id = []
    with new_session() as session:
        output_id = session.execute(select(Run.id).where(Run.save_id == str(game_save)).order_by(Run.id.desc())).first()
    return output_id[0]


def get_specific_run_id(game_save, run_id):
    with new_session() as session:
        return session.execute(
            text('SELECT id FROM Run WHERE id = ' + str(run_id) + ' AND save_id = ' + str(game_save)))


def get_current_level(game_save):
    with new_session() as session:
        return session.execute(text('SELECT level_progress FROM Save WHERE id = ' + str(game_save)))


def get_game_save_language(game_save):
    with new_session() as session:
        return session.execute(text('SELECT language FROM Save WHERE id = ' + str(game_save)))


def get_game_save_keyboard_layout(game_save):
    with new_session() as session:
        return session.execute(text('SELECT keyboard_layout FROM Save WHERE id = ' + str(game_save)))


def get_avg_accuracy_of_specific_char(game_save, char_name):
    """
    Gibt die Genaugkeit für das betreffende Zeichen zurück
    :param game_save: Spielstand
    :param char_name: betreffendes Zeichen
    :return: Genaugkeit für das betreffende Zeichen
    """
    with new_session() as session:
        try:
            count = session.query(func.count(Char.accuracy)).filter(Char.char == char_name and
                Char.run_id == get_last_run_id(str(game_save))).scalar()
            sum_value = session.query(func.sum(Char.accuracy)).filter(Char.char == char_name and
                Char.run_id == get_last_run_id(str(game_save))).scalar()
            return (sum_value / count) * 100
        except TypeError:
            return 0


def get_avg_time_for_specific_char(game_save, char_name):
    """
    Gibt die durchschnittliche Schreib-Zeit für das betreffende Zeichen zurück
    :param game_save: Spielstand
    :param char_name: betreffendes Zeichen
    :return: durchschnittliche Schreib-Zeit für das betreffende Zeichen zurück
    """
    with new_session() as session:
        try:
            count = session.query(func.count(Char.avg_time_per_char)).filter(
                Char.char == char_name and Char.run_id == get_last_run_id(str(game_save))).scalar()
            sum_value = session.query(func.sum(Char.avg_time_per_char)).filter(
                Char.char == char_name and Char.run_id == get_last_run_id(str(game_save))).scalar()
            return sum_value / count
        except TypeError:
            return 0


# Rückgabewert ist ein array (ohne das 2 dimensionale Array mit den Chars), wird zurzeit nicht verwendet
# def show_last_run_results(game_save):
#     last_run_id = get_last_run_id(game_save)
#     with new_session() as session:
#         last_level_played = session.execute(text(
#             'SELECT level_id FROM Run WHERE id = ' + str(last_run_id)
#         ))
#         last_preset_text = session.execute(text(
#             'SELECT preset_text FROM Run WHERE id = ' + str(last_run_id)
#         ))
#         last_typed_text = session.execute(text(
#             'SELECT typed_text FROM Run WHERE id = ' + str(last_run_id)
#         ))
#         last_time_taken_for_level = session.execute(text(
#             'SELECT time FROM Run WHERE id = ' + str(last_run_id)
#         ))
#     return [last_level_played, last_preset_text, last_typed_text, last_time_taken_for_level]

def show_last_char_results(game_save):
    """
    Zeigt die Ergebnisse des letzten Zeichens
    :param game_save: Spielstand
    :return: Array mit Resultaten
    """
    result_array = []
    last_run_id = get_last_run_id(game_save)
    print(last_run_id)
    with new_session() as session:
        char_list = session.execute(text(
            'SELECT char, preset_char_count, typed_char_count, avg_time_per_char, accuracy FROM Char WHERE run_id = ' +
            str(last_run_id)
        ))
    for data_row in char_list:
        result_array.append(data_row)

    return result_array

# wird zurzeit nicht verwendet
# def show_three_best_chars(game_save, search_filter):
#     result_array = []
#     last_run_id = get_last_run_id(game_save)
#     with new_session() as session:
#         char_list = session.execute(text(
#             'SELECT char, preset_char_count, typed_char_count, avg_time_per_char, accuracy FROM Char WHERE run_id = ' +
#             str(last_run_id) + ' ORDER BY ' + search_filter + ' ASC LIMIT 3)'
#         ))
#     for data_row in char_list:
#         result_array.append(data_row)
#
#     return result_array

# wird zurzeit nicht verwendet
# def show_three_worst_chars(game_save, search_filter):
#     result_array = []
#     last_run_id = get_last_run_id(game_save)
#     with new_session() as session:
#         char_list = session.execute(text(
#             'SELECT char, preset_char_count, typed_char_count, avg_time_per_char, accuracy FROM Char WHERE run_id = ' +
#             str(last_run_id) + ' ORDER BY ' + search_filter + ' DESC LIMIT 3)'
#         ))
#     for data_row in char_list:
#         result_array.append(data_row)
#
#     return result_array


def show_time_progression(game_save, char):
    with new_session() as session:
        return list(session.execute(select(Char.avg_time_per_char).join(Char.run).where(Run.save_id == game_save, Char.char == char)))
