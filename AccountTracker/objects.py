'''
defines basic data structure.
'''
from dataclasses import dataclass
from datetime import datetime
from vnpy.trader.object import (
    TradeData,
    OrderData,
    AccountData
)

@dataclass
class BasicData():
    
    balance : float   # 1
    mkv : float   #  1
    leverage : float   #  0
    # holding positions is needed for calculate indicators below
    risk_ratio: float   #  0
    EN_sym: float   #   0
    EN_sec:float   #    0



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


if __name__ == "__main__":
    pass
