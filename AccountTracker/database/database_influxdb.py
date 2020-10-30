from influxdb import InfluxDBClient
from .database import DB_TZ,BaseDBManager,Driver


def init(_:Driver,settings)-> BaseDBManager:
    return 


class InfluxManager(BaseDBManager):

    def __init__(self,host,port, username, password,databse):
        self.influx_client = InfluxDBClient(host,port,username,password,database)
        self.influx_client.create_database(databse)
    
    def __del__(self):
        self.influx_client.close()

    



