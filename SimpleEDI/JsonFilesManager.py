from SimpleEDI.CallsDataBaseManager import CallsDataBaseManager
import datetime
from threading import Lock
from SimpleEDI import Utils
import json


def dict_validation(dictionary):
    all_keys_at_dict = "caller_number" in dictionary.keys() and "destination_number" in dictionary.keys() \
                       and "date_begin" in dictionary.keys() and "date_ending" in dictionary.keys() \
                       and "rate" in dictionary.keys() and "cost" in dictionary.keys()
    if all_keys_at_dict:
        caller_numb_str_type = type(dictionary["caller_number"]) == str
        dest_numb_str_type = type(dictionary["destination_number"]) == str
        date_begin_str_type = type(dictionary["date_begin"]) == str
        date_end_str_type = type(dictionary["date_ending"]) == str
        rate_str_type = type(dictionary["rate"]) == str
        cost_int_type = type(dictionary["cost"]) == int
        if caller_numb_str_type and dest_numb_str_type and date_begin_str_type and date_end_str_type and rate_str_type \
                and cost_int_type:
            try:
                date_begin = datetime.datetime.strptime(dictionary["date_begin"], "%Y-%m-%d %H:%M:%S")
                date_end = datetime.datetime.strptime(dictionary["date_ending"], "%Y-%m-%d %H:%M:%S")
                if date_begin > date_end:
                    return False
            except Exception as exc:
                print(exc)
                return False
            return True
    return False


def data_validation(data):
    if not type(data) == list and not type(data) == dict:
        return False
    if len(data) == 0:
        return False
    if type(data) == dict:
        return dict_validation(data)
    if type(data) == list:
        for item in data:
            if type(item) == dict:
                if not dict_validation(item):
                    return False
    return True


class JsonFilesManager:
    database_manager = None
    file_loading_locker = Lock()

    def __init__(self, dbmanager):
        self.database_manager = dbmanager

    def load_file_to_data_base(self, file_path):
        self.file_loading_locker.acquire()
        if not Utils.check_file_exist(file_path):
            return False
        file = open(file_path, "r")
        try:
            data = json.load(file)
            if not data_validation(data):
                return False
            self.database_manager.insert_call(data["caller_number"], data["destination_number"], data["date_begin"],
                                              data["date_ending"], data["rate"], data["cost"])
            return True
        except Exception as exc:
            print(exc)
            return False
        finally:
            file.close()
            self.file_loading_locker.release()
