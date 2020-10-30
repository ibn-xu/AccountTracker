# AccountTracker
classes for recording financial account data, compute ratios, save to databases


## basic 

Basic information records **regularly**.
Including:

- balance
- mkv
- leverage (mkv / balance)
- risk ratio
- EN_sym(effective number of symbols)
- EN_sec(effective number of sectors)
- black
- metal
- golds
- energy_chemistry
- argiculture
- bond_index
- stock_index


## trade 

records when trade happends,(may not record in time, since trade are available during a whole trading day)


- strategy (for algo trading)
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

- strategy 
- contract
- symbol
- vol
- amount
- exchange
- direction
- offset
- price
- orderid




