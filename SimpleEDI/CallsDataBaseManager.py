import pymysql
from .Rate import Rate
from .CommunicationType import CommunicationType
from enum import Enum
from threading import Lock


class DataBaseConnectionState(Enum):
    SUCCESS = 1
    DATABASE_FAILED = 2
    ERR_AUTH_PARAMS = 3


def check_connection(user, pwd, port, db):
    try:
        connection = pymysql.connect(host="127.0.0.1", user=user, password=pwd, port=port, db=db)
        connection.close()
        return DataBaseConnectionState.SUCCESS
    except pymysql.err.OperationalError as exc:
        print(exc)
        return DataBaseConnectionState.ERR_AUTH_PARAMS
    except pymysql.err.InternalError as exc:
        print(exc)
        return DataBaseConnectionState.DATABASE_FAILED


def create_data_base(user, pwd, port, db):
    connection = pymysql.connect(host="127.0.0.1", user=user, password=pwd, port=port)
    cursor = connection.cursor()
    db_create_query = "CREATE DATABASE {}".format(db)
    cursor.execute(db_create_query)
    db_use_query = "USE {}".format(db)
    cursor.execute(db_use_query)
    com_types_table_query = "CREATE TABLE `communication_type` (\
                            `id` int(11) NOT NULL AUTO_INCREMENT,\
                            `type` varchar(45) NOT NULL,\
                            PRIMARY KEY (`id`)\
                            ) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1"
    cursor.execute(com_types_table_query)
    rates_table_query = "CREATE TABLE `rate` (\
                        `id` int(11) NOT NULL AUTO_INCREMENT,\
                        `name` varchar(45) NOT NULL,\
                        `cost` int(11) NOT NULL,\
                        `type` int(11) DEFAULT NULL,\
                        PRIMARY KEY (`id`)\
                        ) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1"
    cursor.execute(rates_table_query)
    calls_table_query = "CREATE TABLE `call` (\
                        `id` int(11) NOT NULL AUTO_INCREMENT,\
                        `caller_numb` varchar(45) NOT NULL,\
                        `dest_numb` varchar(45) NOT NULL,\
                        `date_begin` datetime NOT NULL,\
                        `date_end` datetime NOT NULL,\
                        `rate` int(11) NOT NULL,\
                        `cost` int NOT NULL,\
                        PRIMARY KEY (`id`)\
                        ) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1"
    cursor.execute(calls_table_query)
    connection.close()


def fill_test_data(user, pwd, port, db):
    connection = pymysql.connect(host="127.0.0.1", user=user, password=pwd, port=port)
    cursor = connection.cursor()
    insert_query = "INSERT INTO {}.communication_type(type) VALUES('GSM')".format(db)
    cursor.execute(insert_query)
    insert_query = "INSERT INTO {}.communication_type(type) VALUES('CDMA')".format(db)
    cursor.execute(insert_query)
    insert_query = "INSERT INTO {}.communication_type(type) VALUES('LTE')".format(db)
    cursor.execute(insert_query)

    id_GSM_query = "SELECT id FROM {}.communication_type WHERE type='GSM'".format(db)
    cursor.execute(id_GSM_query)
    id_GSM = 0
    for row in cursor:
        id_GSM = int(row[0])
    id_CDMA_query = "SELECT id FROM {}.communication_type WHERE type='CDMA'".format(db)
    cursor.execute(id_CDMA_query)
    id_CDMA = 0
    for row in cursor:
        id_CDMA = int(row[0])
    id_LTE_query = "SELECT id FROM {}.communication_type WHERE type='LTE'".format(db)
    cursor.execute(id_LTE_query)
    id_LTE = 0
    for row in cursor:
        id_LTE = int(row[0])

    insert_query = "INSERT INTO {}.rate(name, cost, type) VALUES('Simple', 100, {})".format(db, id_GSM)
    cursor.execute(insert_query)
    insert_query = "INSERT INTO {}.rate(name, cost, type) VALUES('Lite', 250, {})".format(db, id_CDMA)
    cursor.execute(insert_query)
    insert_query = "INSERT INTO {}.rate(name, cost, type) VALUES('Big', 1000, {})".format(db, id_LTE)
    cursor.execute(insert_query)
    connection.commit()
    connection.close()


class CallsDataBaseManager:
    connection = None
    cursor = None
    rate_dict = None
    communication_type_dict = None
    login = None
    password = None
    port = None
    db = None
    main_locker = Lock()

    def __init__(self, login, password, port, db):
        self.login = login
        self.password = password
        self.port = port
        self.db = db
        self.communication_type_dict = self.fetch_comm_types()
        self.rate_dict = self.fetch_rates()

    def open_connection(self):
        self.connection = pymysql.connect(host="127.0.0.1", user=self.login, password=self.password, port=self.port,
                                          db=self.db,
                                          cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.connection.cursor()

    def fetch_comm_types(self):
        self.main_locker.acquire()
        self.open_connection()
        comm_types = dict()
        query = "SELECT id, type FROM {}.communication_type;".format(self.db)
        self.cursor.execute(query)
        self.close_connection()
        for row in self.cursor:
            comm_types[row["id"]] = CommunicationType(row["id"], row["type"])
        self.main_locker.release()
        return comm_types

    def fetch_rates(self):
        self.main_locker.acquire()
        self.open_connection()
        rate_dict = dict()
        query = "SELECT id, name, cost, type FROM {}.rate;".format(self.db)
        self.cursor.execute(query)
        self.close_connection()
        for row in self.cursor:
            if self.get_com_type_by_id(row["type"]) is not None:
                rate_dict[row["name"]] = Rate(row["id"], row["name"], self.get_com_type_by_id(row["type"]), row["cost"])
        self.main_locker.release()
        return rate_dict

    def get_calls_dict_by_number(self, number):
        self.main_locker.acquire()
        self.open_connection()
        query = "SELECT `call`.`id`, `call`.`caller_numb`,\
                `call`.`dest_numb`,\
                `call`.`date_begin`,\
                 `call`.`date_end`,\
                 `rate`.`name`,\
                 `call`.`cost`\
                 FROM {}.`call` INNER JOIN {}.`rate` ON \
                `call`.`rate` = `rate`.`id` WHERE `call`.caller_numb = \'{}\' or `call`.dest_numb = \'{}\';".format(
            self.db,
            self.db,
            number,
            number
        )
        self.cursor.execute(query)
        calls_dict = dict()
        for row in self.cursor:
            calls_dict[row["id"]] = {"CALLER_NUMBER": row["caller_numb"], "DESTINATION_NUMBER": row["dest_numb"],
                                     "BEGIN_DATE": row["date_begin"], "END_DATE": row["date_end"], "RATE": row["name"],
                                     "COST": row["cost"]}
        self.close_connection()
        self.main_locker.release()
        return calls_dict

    def rate_is_exist(self, name):
        return name in self.rate_dict.keys()

    def com_type_is_exist(self, com_id):
        return com_id in self.communication_type_dict.keys()

    def get_com_type_by_id(self, com_id):
        if not self.com_type_is_exist(com_id):
            return None
        return self.communication_type_dict[com_id]

    def get_rate_by_name(self, name):
        if not self.rate_is_exist(name):
            return None
        return self.rate_dict[name]

    def insert_call(self, caller_number, destination_number, date_begin, date_end, rate_name, cost):
        self.main_locker.acquire()
        if not self.rate_is_exist(rate_name):
            return
        rate_id = self.get_rate_by_name(rate_name).get_id()
        self.open_connection()
        query = "INSERT INTO {}.call (caller_numb, dest_numb, date_begin, date_end, rate, cost) VALUES({}, {}, {}, " \
                "{}, {}, {});".format(
                                    self.db,
                                    '"' + caller_number + '"',
                                    '"' + destination_number + '"',
                                    '"' + date_begin + '"',
                                    '"' + date_end + '"',
                                    rate_id,
                                    cost)
        self.cursor.execute(query)
        self.connection.commit()
        self.close_connection()
        self.main_locker.release()

    def close_connection(self):
        self.connection.close()
