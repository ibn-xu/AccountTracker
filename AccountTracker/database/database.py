from abc import ABC,abstractmethod
from pytz import timezone
from enum import  Enum
from ..settings import database_set
from datetime import datetime

DB_TZ = timezone(database_set['timezone'])

class Driver(Enum):
    SQLITE = 'sqlite'
    MYSQL = 'mysql'
    POSTGRESQL = 'postgresql'
    MONGODB = 'mongodb'
    INFLUX = 'influxdb'

class BaseDBManager(ABC):
    
    @abstractmethod
    def save_data(self,data,dt=datetime.now()):
        '''
        basic data: use current dt
        trade/order data: use datetime in Object
        '''

        pass

    @abstractmethod
    def update_account(self,accounts:dict):
        pass

    @abstractmethod
    def regular_work(self):
        pass

    @abstractmethod
    def update_basic(self,mkv,risk_ratio,positions:dict):
        pass

    @abstractmethod
    def update_trade(self,tradedata:dict):
        pass


    @abstractmethod
    def update_order(self,orderdata:dict):
        pass


