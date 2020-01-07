class CommunicationType:
    type_id = None
    name = None

    def __init__(self, type_id, name):
        self.type_id = type_id
        self.name = name

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_id(self):
        return self.type_id

    def set_id(self, type_id):
        self.type_id = type_id
