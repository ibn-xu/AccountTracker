from time import sleep
from vnpy.app.script_trader import ScriptEngine
import pandas as pd
from AccountTracker.database.database_influxdb import init
from AccountTracker.settings import database_set


dbmanager = init(1,database_set)


def run(engine: ScriptEngine):
    """
    脚本策略的主函数说明：
    1. 唯一入参是脚本引擎ScriptEngine对象，通用它来完成查询和请求操作
    2. 该函数会通过一个独立的线程来启动运行，区别于其他策略模块的事件驱动
    3. while循环的维护，请通过engine.strategy_active状态来判断，实现可控退出

    监控账户，保存数据到influxdb

    """

    # for comparing with latest records

    __subscribe_list = []
    all_contract = 0
    # 持续运行，使用strategy_active来判断是否要退出程序
    while engine.strategy_active:
        if all_contract.empty:
            all_contract = engine.get_all_contracts(True)[['vt_symbol','size']]
        # 主观策略用统一的ID
        # 程序化交易各自有id区分

        df = engine.get_all_accounts()
        bal = df[0].balance
        ava = df[0].available

        # mkv

        initial_pos = engine.get_all_positions(True)
        # 过滤不正常合约（套利合约）
        contracts_bool = initial_pos['vt_symbol'].str.contains('&')
        current_pos = initial_pos[~contracts_bool]
        current_pos_str = current_pos.to_json(orient='columns',force_ascii=False)
        if not (current_pos is None):
            current_contract = list(current_pos['vt_symbol'])

            # 有差异的合约
            diff_contract = [x for x in current_contract if x not in __subscribe_list]
            if len(diff_contract)>0:
                engine.subscribe(vt_symbols=diff_contract)
                __subscribe_list[:] = current_contract[:]
                sleep(1)
            
            # 获取持仓信息： 手数 与 最新价
            latest_prices = engine.get_ticks(vt_symbols=__subscribe_list,use_df=True)[['last_price','vt_symbol']]
            while not latest_prices.all().all():
                sleep(0.2)
                latest_prices = engine.get_ticks(vt_symbols=__subscribe_list,use_df=True)[['last_price','vt_symbol']]

            latest_volumns = current_pos[['vt_symbol','volume','direction']]
            

            tmp_df = pd.merge(left=latest_prices,right=latest_volumns,on='vt_symbol',how='inner')
            final_df = pd.merge(left=tmp_df,right=all_contract,on='vt_symbol',how='inner')
            final_df['mk_value'] = final_df['last_price'] * final_df['volume'] * final_df['size']
            local_mkvalue = final_df['mk_value'].sum()

            # EN calculate

            final_df['weights'] = final_df['mk_value'] / local_mkvalue

            s = 0

            for f in final_df['weights']:
                s += f**2

            EN_sym = 1/ s


            # return local_mkvalue
        else:
            local_mkvalue = 0

    # risk_ratio
        holding_pnl = sum([a.pnl for (_,a) in current_pos.iterrows()])
        risk_ratio2 = (bal - ava - holding_pnl) / bal
        risk_ratio1 = 1 - ava / bal

        if holding_pnl < 0:
            risk_ratio = risk_ratio1
        else:
            risk_ratio = risk_ratio2


    # acc data

        acc_dict = engine.main_engine.engines['oms'].accounts.copy()
        dbmanager.update_account(accounts=acc_dict)


    # basic data
        # pos_dict = engine.main_engine.engines['oms'].positions.copy()
        dbmanager.update_basic(mkv=local_mkvalue,risk_ratio=risk_ratio,EN_sym=EN_sym)



    # order data
        order_dict = engine.main_engine.engines['oms'].orders.copy()
        dbmanager.update_order(orderdata=order_dict)
    # trade data
        trade_dict = engine.main_engine.engines['oms'].trades.copy()
        dbmanager.update_trade(tradedata=trade_dict)


        # 等待x秒进入下一轮
        sleep(10)




