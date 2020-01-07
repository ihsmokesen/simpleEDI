import collections
from threading import Lock
from SimpleEDI import Utils


class FilesStateInfoContainer:
    dump_path = ""
    files_name_list = set()
    list_locker = Lock()
    dump_locker = Lock()

    def __init__(self, dump_path):
        self.dump_path = dump_path
        self.init_list()

    def remove_element(self, element):
        self.list_locker.acquire()
        try:
            self.files_name_list.remove(element)
            return
        except Exception as exc:
            print(exc)
        finally:
            self.list_locker.release()

    def append_list(self, file_name):
        self.list_locker.acquire()
        try:
            self.files_name_list.add(file_name)
            return
        except Exception as exc:
            print(exc)
        finally:
            self.list_locker.release()

    def init_list(self):
        self.files_name_list.clear()
        if not Utils.check_path_exist(self.dump_path):
            dump_file = open(self.dump_path, "w")
            dump_file.close()
        dump_file = open(self.dump_path, "r")
        file_names = dump_file.read().split("\n")
        for file_name in file_names:
            if not file_name == "":
                self.append_list(file_name)
        dump_file.close()

    def get_list(self):
        return self.files_name_list

    def dump_list(self):
        self.dump_locker.acquire()
        try:
            dump_file = open(self.dump_path, "w")
            for file_name in self.files_name_list:
                dump_file.write(file_name + "\n")
            dump_file.close()
        except Exception as exc:
            print(exc)
        finally:
            self.dump_locker.release()
