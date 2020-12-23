# AccountTracker : AccMonitor_script2.py
classes for recording financial account data, compute ratios, save to databases

NOTE: currently tracking *CTP*  accounts in *basic* data.

## basic 

Basic information records **regularly**.
Including:

- balance
- mkv
- leverage (mkv / balance)
- risk ratio
- EN_sym(effective number of symbols)
- ~~EN_sec(effective number of sectors)~~
- pnl : floating gain/loss of futures
- option_pnl : floating gain/loss of options



## trade 

records when trade happends,(may not record in time, since trade are available during a whole trading day)


- reference (reference for inentify strategies)
- datetime
- contract 合约 e.g. rb2101
- symbol   品种 e.g.  rb
- vol
- amount
- exchange
- direction
- offset
- price
- orderid
- tradeid


## order

records order when orders are sent.

- reference (reference for inentify strategies)
- contract
- symbol
- vol
- amount
- exchange
- direction
- offset
- price
- orderid


## position record

- save daily position under *positionRecords* folder(auto create).
- named by date: '20201102.json'


# OTC pnl & Net value : NV_otc.py

## OTC pnl

- read position table:
    - get pre-settlement price for pre-day balance
    - rt price of underlying contract for **pnl**
- read outsource data:
    - forengn account (chg)
    - total balance (pre-day)
    - product share
- **Net value** calculate & write
    - read *futures pnl* 
    - calculate NV, save to *influxdb*


# Net Value Alarm:

