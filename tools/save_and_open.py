import json
from database import new_session, Save, Run, Char
from sqlalchemy import update, select

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


def save_to_json_file(red, blue, green, volume, windowsize, screenfull):
    with open('settings.json', 'w', encoding='utf-8') as f:
        json.dump([red, green, blue, volume, windowsize, screenfull], f, ensure_ascii=False, indent=5)


# returns an array with the information's in the JSON file
def get_info_from_json_file():
    data = json.load(open('settings.json'))
    return data


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


# -----------------Noch testen---------------------
def save_game(game_save_nr, level_id, preset_text, written_text, time_needed_for_game, char_array):
    with new_session() as session:
        r = Run(
            save_id=game_save_nr,
            level_id=level_id,
            preset_text=preset_text,
            typed_text=written_text,
            time_taken_for_level=time_needed_for_game,
        )

        session.add(r)

        id_run = get_last_run_id(game_save_nr)
        session.commit()

    for data in char_array:
        accuracy = 0  # 0-1 --> 1==100%
        if data[2] >= data[1]:
            # sinnvoll ob über 100% genauigkeit = 100% genauigkeit sind? 110% sind ja auch fehler no?
            accuracy = 1
        else:
            accuracy = data[2] - data[1]

        with new_session() as session:
            c = Char(
                run_id=id_run,
                char=data[0],
                preset_char_count=data[1],
                typed_char_count=data[2],
                avg_time_per_char=data[3],
                accuracy=accuracy,
            )

            session.add(c)
            session.commit()


# Nicht wirklich sicher, ob das geht, da das MySQL statt SQL code ist
def get_last_run_id(game_save):
    with new_session() as session:
        return session.execute("SELECT id FROM Run WHERE save_id = " + game_save + "ORDER BY id DESC LIMIT 1")


def get_specific_run_id(game_save, run_id):
    with new_session() as session:
        return session.execute("SELECT id FROM Run WHERE id =" + run_id + " AND save_id =" + game_save)


def get_current_level(game_save):
    with new_session() as session:
        return session.execute("SELECT level_progress FROM Save WHERE id =" + game_save)


def get_game_save_language(game_save):
    with new_session() as session:
        return session.execute("SELECT language FROM Save WHERE id =" + game_save)


def get_game_save_keyboard_layout(game_save):
    with new_session() as session:
        return session.execute("SELECT keyboard_layout FROM Save WHERE id =" + game_save)


def get_game_save_average_accuracy(game_save):
    with new_session() as session:
        value_of_accuracy_sum = session.execute(
            "SELECT SUM(accuracy) FROM Char WHERE run_id = (SELECT save_id FROM Run WHERE save_id =" + game_save + ")"
        )
        count_of_runs = session.execute(
            "SELECT COUNT(accuracy) FROM Char WHERE run_id = (SELECT save_id FROM Run WHERE save_id =" + game_save + ")"
        )
        average_accuracy = value_of_accuracy_sum / count_of_runs
    return average_accuracy


def get_avg_time_for_specific_char(game_save, char_name):
    with new_session() as session:
        summed_time_for_char = session.execute(
            "SELECT COUNT(avg_time_per_char) FROM Char WHERE char = " +
            char_name + "and run_id = (SELECT save_id FROM Run WHERE save_id =" +
            game_save + ")"
        )
    return summed_time_for_char / get_last_run_id(game_save)


# Rückgabewert ist ein array (ohne das 2 dimensionale Array mit den Chars)
def show_last_run_results(game_save):
    last_run_id = get_last_run_id(game_save)
    with new_session() as session:
        last_level_played = session.execute(
            "SELECT level_id FROM Run WHERE id =" + last_run_id
        )
        last_preset_text = session.execute(
            "SELECT preset_text FROM Run WHERE id =" + last_run_id
        )
        last_typed_text = session.execute(
            "SELECT typed_text FROM Run WHERE id =" + last_run_id
        )
        last_time_taken_for_level = session.execute(
            "SELECT time_taken_for_level FROM Run WHERE id =" + last_run_id
        )
    return [last_level_played, last_preset_text, last_typed_text, last_time_taken_for_level]


def show_last_char_results(game_save):
    result_array = []
    last_run_id = get_last_run_id(game_save)
    with new_session() as session:
        char_list = session.execute(
            "SELECT char, preset_char_count, typed_char_count, vg_time_per_char FROM Char WHERE run_id =" +
            last_run_id +
            ")"
        )
    for data_row in char_list:
        result_array.append(data_row)

    return result_array


def show_three_best_chars(game_save, search_filter):
    result_array = []
    last_run_id = get_last_run_id(game_save)
    with new_session() as session:
        char_list = session.execute(
            "SELECT char, preset_char_count, typed_char_count, vg_time_per_char FROM Char WHERE run_id =" +
            last_run_id + " ORDER BY " + search_filter + " ASC LIMIT 3)"
        )
    for data_row in char_list:
        result_array.append(data_row)

    return result_array


def show_three_worst_chars(game_save, search_filter):
    result_array = []
    last_run_id = get_last_run_id(game_save)
    with new_session() as session:
        char_list = session.execute(
            "SELECT char, preset_char_count, typed_char_count, vg_time_per_char FROM Char WHERE run_id =" +
            last_run_id + " ORDER BY " + search_filter + "DESC LIMIT 3)"
        )
    for data_row in char_list:
        result_array.append(data_row)

    return result_array
