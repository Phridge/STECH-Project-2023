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
    twod_char_array = db.show_last_run_results(game_save)
    output_array = [0, 0, 0, 0]
    for data in twod_char_array:
        if data[0] == char_name:
            output_array = data
            break
    return output_array


# provides the user stats of the last game the user played for all chars
def get_data_for_bigu_grapu(game_save):
    twod_char_array = db.show_last_run_results(game_save)
    output_array = [0, 0, 0, 0]
    for data in twod_char_array:
        output_array[0] = data[0]
        output_array[1] = data[2]
        output_array[2] = data[3]
        output_array[3] = data[4]
    return output_array
