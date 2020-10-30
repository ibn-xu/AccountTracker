'''
defines basic data structure.
'''
from dataclasses import dataclass





@dataclass
class BasicData():
    
    balance : float
    mkv : float
    leverage : float
    risk_ratio: float
    EN_sym: float
    EB_sec:float
    black : float
    metal : float
    golds : float
    energy_chemistry : float
    argiculture : float
    bond_index : float
    stock_index : float




@dataclass
class TradeData():
    strategy
    datetime
    contract
    symbol  
    vol
    # amount
    exchange
    direction
    offset
    price
    orderid
    tradeid

@dataclass
class OrderData():
    strategy 
    contract
    symbol
    vol
    # amount
    exchange
    direction
    offset
    price
    orderid


if __name__ == "__main__":
    pass
