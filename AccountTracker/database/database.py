from abc import ABC,abstractmethod
from pytz import timezone
from enum import  Enum
from ..settings import database_set

DB_TZ = timezone(database_set['timezone'])

class Driver(Enum):
    SQLITE = 'sqlite'
    MYSQL = 'mysql'
    POSTGRESQL = 'postgresql'
    MONGODB = 'mongodb'
    INFLUX = 'influxdb'

class BaseDBManager(ABC):
    
    @abstractmethod
    def save_data(self):
        pass


    @abstractmethod
    def regular_work(self):
        pass

    @abstractmethod
    def update_basic(self):
        pass

    @abstractmethod
    def update_trade(self):
        pass


    @abstractmethod
    def update_order(self):
        pass


