class Rate:
    rate_id = None
    name = None
    communication_type = None
    cost = None

    def __init__(self, rate_id, name, communication_type, cost):
        self.rate_id = rate_id
        self.name = name
        self.type = communication_type
        self.cost = cost

    def get_id(self):
        return self.rate_id

    def set_id(self, rate_id):
        self.rate_id = rate_id

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_type(self):
        return self.communication_type

    def set_type(self, com_type):
        self.communication_type = com_type

    def get_cost(self):
        return self.cost

    def set_cost(self, cost):
        self.cost = cost
