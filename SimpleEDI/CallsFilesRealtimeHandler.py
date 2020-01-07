from watchdog.events import FileSystemEventHandler
from SimpleEDI import Utils


class CallsFilesRealtimeHandler(FileSystemEventHandler):
    files_dir_path = ""
    info_container = None
    json_file_manager = None

    def __init__(self, info_container, json_file_manager, files_dir_path):
        super(CallsFilesRealtimeHandler, self).__init__()
        self.set_files_dir_path(files_dir_path)
        self.json_file_manager = json_file_manager
        self.info_container = info_container

    def set_files_dir_path(self, files_dir_path):
        self.files_dir_path = files_dir_path

    def get_files_dir_path(self):
        return str(self.files_dir_path)

    def on_created(self, event):
        path = event.src_path
        if event.is_directory is True or not Utils.get_directory_from_path(path) == self.files_dir_path:
            return
        name = Utils.get_file_name_from_path(path)
        if Utils.get_file_size(path) == 0:
            return
        state = self.json_file_manager.load_file_to_data_base(path)
        if state:
            self.info_container.append_list(name)

    def on_deleted(self, event):
        path = event.src_path
        if event.is_directory is True or not Utils.get_directory_from_path(path) == self.files_dir_path:
            return
        name = Utils.get_file_name_from_path(path)
        if name in self.info_container.get_list():
            self.info_container.remove_element(name)

    def on_moved(self, event):
        if event.is_directory is True:
            return
        path = event.src_path
        new_path = event.dest_path
        name = Utils.get_file_name_from_path(path)
        new_dir = Utils.get_directory_from_path(new_path)
        new_name = Utils.get_file_name_from_path(new_path)
        if name in self.info_container.get_list() and Utils.get_file_size(path) > 0:
            self.info_container.remove_element(name)
            if not new_dir == self.files_dir_path:
                return
            self.info_container.append_list(new_name)

    def on_modified(self, event):
        path = event.src_path
        if event.is_directory is True or not Utils.get_directory_from_path(path) == self.files_dir_path:
            return
        name = Utils.get_file_name_from_path(path)
        if name not in self.info_container.get_list():
            state = self.json_file_manager.load_file_to_data_base(path)
            if state:
                self.info_container.append_list(name)

