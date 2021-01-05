'''
defines basic data structure.
'''
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from vnpy.trader.object import (
    TradeData,
    OrderData,
    AccountData
)

@dataclass
class BasicData():
    
    balance : float   # 1
    mkv : float   #  1
    mkv_long : float   #  1
    mkv_short : float   #  1
    mkv_agri : float   # 1
    mkv_bond : float   # 1
    mkv_stock : float   # 1
    mkv_metal : float   # 1
    mkv_gold : float   # 1
    mkv_energy : float   # 1
    mkv_black : float   # 1
    leverage : float   #  0
    # holding positions is needed for calculate indicators below
    risk_ratio: float   #  0
    EN_sym: float   #   0
    pnl: float
    option_pnl : float
    option_balance :float



@dataclass
class TradeData3000(TradeData):
    reference: str = '' 


# @dataclass
# class OrderData():
#     reference : str 
#     contract : str
#     symbol : str
#     vol : int
#     # amount
#     exchange : str
#     direction : str
#     offset : str
#     price : float
#     orderid : str

class Sector(Enum):
    """
    futures sectors
    """
    Agri = '农产品'
    Bond = '债券'
    Stock = '股指'
    Energy = '能源'
    Metal = '有色'
    Gold = '贵金属'
    Black = '黑色'


if __name__ == "__main__":
    pass
