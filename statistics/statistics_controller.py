import tools.save_and_open as db

"""
-------------Controller File-----------
For: statistic_view.py
----------------------------------------
"""


# provides the id of the game
def get_last_run_id(game_save):
    return db.get_last_run_id(game_save)


# provides the current level the player was in
def get_current_level(game_save):
    return db.get_current_level(game_save)


# provides the average time needed for a specific char
def get_avg_time_for_char(game_save, char_name):
    return db.get_avg_time_for_specific_char(game_save, char_name)


# provides the average accuracy for a specific char
def get_avg_accuracy_for_char(game_save, char_name):
    return db.get_avg_accuracy_of_specific_char(game_save, char_name)


# provides the user stats of the last game the user played for one specific char
def get_last_results_of_char(game_save, char_name):
    twod_char_array = db.show_last_char_results(game_save)
    # [char, preset_char_count, typed_char_count, avg_time_per_char, accuracy]
    output_array = [0, 0, 0, 0, 0]
    for data in twod_char_array:
        if data[0] == char_name:
            output_array = data
            break
    return output_array


# provides the user stats of the last game the user played for all chars
def get_data_for_bigu_grapu(game_save):
    twod_char_array = db.show_last_char_results(game_save)
    output_array = []
    for data_row in twod_char_array:
        output_array.append(data_row)
    return output_array


def get_count_of_chars_in_array(game_save):
    twod_char_array = db.show_last_char_results(game_save)
    i = 0
    count_array = []
    for data_row in twod_char_array:
        i += 1
        count_array.append(i)
    return count_array


def get_last_accuracy_of_all_chars(game_save):
    twod_char_array = get_data_for_bigu_grapu(game_save)
    accuracy_array = []
    for data_row in twod_char_array:
        accuracy_array.append(data_row[4])
    return accuracy_array * 100


def get_last_time_of_all_chars(game_save):
    twod_char_array = get_data_for_bigu_grapu(game_save)
    time_array = []
    for data_row in twod_char_array:
        time_array.append(data_row[3])
    return time_array


def get_last_user_input_of_all_chars(game_save):
    twod_char_array = get_data_for_bigu_grapu(game_save)
    char_typed_array = []
    for data_row in twod_char_array:
        char_typed_array.append(data_row[2])
    return char_typed_array


def get_time_progression(game_save, char_name):
    time_list = db.show_time_progression(game_save, char_name)
    output_array = []
    for x in time_list:
        output_array.append(round(x[0]*1000))
    return output_array


# return db.show_time_progression(game_save, char_name)


def get_avg_time_per_char_array(game_save, char_name):
    time_list = db.show_time_progression(game_save, char_name)
    avg_time = get_avg_time_for_char(game_save, char_name)
    output_array = []
    for x in time_list:
        output_array.append(round(avg_time * 1000))
    return output_array


def get_count_with_char(game_save, char_name):
    time_list = db.show_time_progression(game_save, char_name)
    i = 0
    output_array = []
    for x in time_list:
        i += 1
        output_array.append(i)
    return output_array
