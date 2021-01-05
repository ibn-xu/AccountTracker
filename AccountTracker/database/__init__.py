''''''

from .database import BaseDBManager, Driver


def init(settings) -> BaseDBManager:
    driver = Driver(settings['driver'])
    if driver is Driver.MONGODB:
        return init_mongo(driver, settings)
    elif driver is Driver.INFLUX:
        return init_influx(driver, settings)
    else:
        return init_sql(driver, settings)


def init_sql(driver: Driver, settings):
    return None


def init_mongo(driver: Driver, settings):
    return None


def init_influx(driver: Driver, settings):
    from .database_influxdb import init
    _database_manager = init(driver, settings)
    return _database_manager
