from .database import DB_TZ,BaseDBManager,Driver

def init(Driver,settings:dict)->BaseDBManager:
    return None