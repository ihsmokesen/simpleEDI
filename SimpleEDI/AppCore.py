from SimpleEDI.CallsFilesRealtimeHandler import CallsFilesRealtimeHandler
from SimpleEDI.FilesStateInfoContainer import FilesStateInfoContainer
from watchdog.observers import Observer
from SimpleEDI import Utils
from SimpleEDI.JsonFilesManager import JsonFilesManager
from SimpleEDI import CallsDataBaseManager as cdbm
from configparser import ConfigParser
from SimpleEDI.CallsGetRequestHandler import CallsGetRequestHandler
from SimpleEDI.ShutdownGetRequestHandler import ShutdownGetRequestHandler


def set_config(config_path):
    config = ConfigParser()
    config.add_section("GENERAL")
    config.set("GENERAL", "observer_directory_path", "info")
    config.set("GENERAL", "data_base_login", "root")
    config.set("GENERAL", "data_base_password", "1234")
    config.set("GENERAL", "data_base_port", "3306")
    config.set("GENERAL", "data_base_name", "callsdb")
    file = open(config_path, "w")
    config.write(file)
    file.close()


def config_dict_validation(config_dict):
    path_in_dict = "observer_directory_path" in config_dict.keys()
    login_in_dict = "data_base_login" in config_dict.keys()
    pwd_in_dict = "data_base_password" in config_dict.keys()
    port_in_dict = "data_base_port" in config_dict.keys()
    name_in_dict = "data_base_name" in config_dict.keys()
    if not path_in_dict or not login_in_dict or not pwd_in_dict or not port_in_dict or not name_in_dict:
        return False
    path_not_null = not config_dict["observer_directory_path"] is None
    login_not_null = not config_dict["data_base_login"] == "" and not config_dict["data_base_login"] is None
    pwd_not_null = not config_dict["data_base_password"] is None
    port_not_null = not config_dict["data_base_port"] is None
    name_not_null = not config_dict["data_base_name"] == "" and not config_dict["data_base_name"] is None
    if path_not_null and login_not_null and pwd_not_null and port_not_null and name_not_null:
        return True
    return False


def get_config_general_section(config_path):
    config = ConfigParser()
    config.read(config_path)
    config_dict_general = {s: dict(config.items(s)) for s in config.sections()}
    config_dict = config_dict_general["GENERAL"]
    return config_dict


class AppCore:
    FILES_STATE_INFO_DUMP_PATH = "DIRECTORY_STATE.dat"
    CONFIG_FILE_PATH = "config.ini"
    info_container = None
    json_file_manager = None
    observer_handler = None
    observer_obj = None
    files_dir_path = ""
    calls_get_handler = None
    shutdown_handler = None

    def __init__(self):
        if not Utils.check_path_exist(self.CONFIG_FILE_PATH):
            print("Config file is missing! Creating config with default parameters...")
            set_config(self.CONFIG_FILE_PATH)
        config_dict = get_config_general_section(self.CONFIG_FILE_PATH)
        if not config_dict_validation(config_dict):
            print("Config file is incorrect! Exit...")
            return
        self.files_dir_path = config_dict["observer_directory_path"]
        if not Utils.check_path_exist(self.files_dir_path):
            print("Directory is missing! Please specify directory! Exit...")
            return
        db_login = config_dict["data_base_login"]
        db_password = config_dict["data_base_password"]
        db_port = int(config_dict["data_base_port"])
        db_name = config_dict["data_base_name"]
        connection_result = cdbm.check_connection(db_login, db_password, db_port, db_name)
        if connection_result is not cdbm.DataBaseConnectionState.SUCCESS:
            if connection_result == cdbm.DataBaseConnectionState.DATABASE_FAILED:
                print("The database has been lost. The program will restore the database")
                try:
                    cdbm.create_data_base(db_login, db_password, db_port, db_name)
                    cdbm.fill_test_data(db_login, db_password, db_port, db_name)
                except Exception as exc:
                    print(exc)
                    return
            else:
                print("Error connecting to database! Recheck the connection settings in the ini file")
                return
        database_manager = cdbm.CallsDataBaseManager(db_login, db_password, db_port, db_name)
        self.calls_get_handler = CallsGetRequestHandler(database_manager)
        self.calls_get_handler.start()
        self.shutdown_handler = ShutdownGetRequestHandler(self)
        self.shutdown_handler.start()
        self.json_file_manager = JsonFilesManager(database_manager)
        self.info_container = FilesStateInfoContainer(self.FILES_STATE_INFO_DUMP_PATH)
        self.initial_check()
        self.observer_handler = CallsFilesRealtimeHandler(self.info_container, self.json_file_manager,
                                                          self.files_dir_path)
        self.observer_obj = Observer()
        self.observer_obj.schedule(self.observer_handler, self.files_dir_path, True)

    def initial_check(self):
        if self.files_dir_path is None:
            return
        current_files_name_set = set()
        for file_name in Utils.get_all_file_names(self.files_dir_path):
            current_files_name_set.add(file_name)
        dumped_files_name_set = self.info_container.get_list()
        set_to_upd = current_files_name_set.difference(dumped_files_name_set)
        set_to_delete = dumped_files_name_set.difference(current_files_name_set)
        for file_name in set_to_delete:
            self.info_container.remove_element(file_name)
        for file_name in set_to_upd:
            new_file_path = self.files_dir_path + "\\" + file_name
            state = self.json_file_manager.load_file_to_data_base(new_file_path)
            if state:
                self.info_container.append_list(file_name)
        self.info_container.dump_list()

    def get_files_dir_path(self):
        return str(self.files_dir_path)

    def set_files_dir_path(self, files_dir_path):
        self.files_dir_path = files_dir_path

    def start_realtime_observer(self):
        if self.observer_obj is not None:
            self.observer_obj.start()

    def stop_realtime_observer(self):
        if self.observer_obj is not None:
            self.observer_obj.stop()
            self.observer_obj.join()

    def finish_all(self):
        self.stop_realtime_observer()
        self.save()

    def save(self):
        if self.info_container is not None:
            self.info_container.dump_list()
