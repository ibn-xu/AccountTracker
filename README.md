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




