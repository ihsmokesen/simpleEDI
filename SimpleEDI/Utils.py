import os
import json
from json import JSONDecodeError


def check_file_exist(file_path):
    if check_path_exist(file_path):
        if os.path.isfile(file_path):
            return True
    return False


def check_path_exist(path):
    if os.path.exists(path):
        return True
    return False


def get_all_file_names(path):
    return os.listdir(path)


def get_file_name_from_path(path):
    name = ""
    for index in range(len(path) - 1, -1, -1):
        if path[index] == "\\":
            break
        name = path[index] + name
    return name


def get_file_size(file_path):
    return os.path.getsize(file_path)


def get_directory_from_path(path):
    return os.path.dirname(path)


def get_json_from_file(path):
    if not check_path_exist(path) or not check_file_exist(path):
        return None
    file = open(path, "r")
    try:
        data = json.load(file)
        return data
    except JSONDecodeError as err:
        print(err)
        return None
    finally:
        file.close()