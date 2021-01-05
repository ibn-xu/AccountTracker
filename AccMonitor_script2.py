from time import sleep
import pathlib
import datetime
import pandas as pd
import trading_calendars
from vnpy.app.script_trader import ScriptEngine
from vnpy.trader.constant import Direction
from AccountTracker.database.database_influxdb import init
from AccountTracker.settings import database_set
from AccountTracker.settings import acc_folder


DAY_END = datetime.time(15, 15)
NIGHT_START = datetime.time(20, 50, 0)
NIGHT_END = datetime.time(3, 0, 0)

delta = datetime.timedelta(milliseconds=1)
dbmanager = init(1, database_set)

# Get public sessions data from Shanghai Stock Exchange
cn_calendar = trading_calendars.get_calendar('XSHG')
# sessions is datetime.date
sessions = [x.to_pydatetime().date() for x in cn_calendar.all_sessions]

try:
    outsource_df = pd.read_csv(acc_folder['jinshan'],
                               parse_dates=['start', 'end'])
except:
    outsource_df = None


def option_picker(s: str):
    '''
    s: rb2101.SHFE(vt_symbol)

    if s is option, return basic str e.g: DCE.i2009-C-650
    if s is SPC, skip it(tqsdk get no kline). e.g DCE.SPC a2101&m2101 
    '''

    if '&' in s:
        return None
    if len(s) > 12:
        # options
        # print('场内期权', s)
        return s


def tradeTime_TRANS(dd: dict):
    '''
    modify trade/order date: **for CTP gateway**

    if trades happen at night: modify to previous date
    if trades happen at day: save previous date;
    '''
    if dd:
        for k, v in dd.items():

            if v.datetime.time() > NIGHT_START or v.datetime.time() < NIGHT_END:
                # needs modify
                tmp_index = sessions.index(v.datetime.date())
                actual_date = sessions[tmp_index-1]
                dd[k].datetime = v.datetime.replace(
                    year=actual_date.year, month=actual_date.month, day=actual_date.day)


def check_timestamp(d: dict):
    '''
    input tradedict and/or orderdict.

    if data in d has same timestamp, modify them to avoid overriding data in influxdb.

    +1ms +2ms and so on.
    '''
    if d:
        unique_timestamp = []

        i = 1
        sorted_key = list(d.keys())
        sorted_key.sort()

        for k in sorted_key:
            v = d[k]
            if v.datetime in unique_timestamp:
                v.datetime += delta * i
                i += 1
            unique_timestamp.append(v.datetime)


def run(engine: ScriptEngine):
    """
    脚本策略的主函数说明：
    1. 唯一入参是脚本引擎ScriptEngine对象，通用它来完成查询和请求操作
    2. 该函数会通过一个独立的线程来启动运行，区别于其他策略模块的事件驱动
    3. while循环的维护，请通过engine.strategy_active状态来判断，实现可控退出

    监控账户，保存数据到influxdb

    ****    CTP接口   ****
    A. order日期时间是报单的实际时间，但是trade回报中，夜盘成交的日期是交易日的日期，而不是实际成家的日期（时间是准确的）

    因此需要做一个转换：
    1. 夜盘成交 => 必然是夜盘挂单 => 根据orderid调整日期（不改时间）
    2. 白天成交 => 不修改

    B. trade中，多笔成交可能在同一个时间戳下返回，因此后写入的trade会覆盖之前的一个记录：
    1. 写入之前，检查时间是否相同，直接修改时间：500ms之内比如+1ms，+2ms等

    """

    # for comparing with latest records

    __subscribe_list = []
    all_contract = pd.DataFrame()
    # 持续运行，使用strategy_active来判断是否要退出程序
    while engine.strategy_active:

        futures_pnl = 0.0
        option_pnl = 0.0
        option_balance = 0.0
        mkv_long = 0.0
        mkv_short = 0.0

        if all_contract.empty:
            all_contract = engine.get_all_contracts(
                True)[['vt_symbol', 'size']]

            contract_size = dict(
                zip(all_contract['vt_symbol'], all_contract['size']))
        # 主观策略用统一的ID
        # 程序化交易各自有id区分

        df = engine.get_all_accounts()
        bal = df[0].balance
        ava = df[0].available
        EN_sym = 0.0

        # mkv

        initial_pos = engine.get_all_positions(True)
        if not (initial_pos is None):
            # 过滤不正常合约（套利合约）
            contracts_bool = initial_pos['vt_symbol'].str.contains('&')
            current_pos = initial_pos[~contracts_bool]

            if outsource_df is None:
                futures_pnl = 0.0
            else:
                futures_pnl = bal - outsource_df.loc[0]['presettle_futures']
            # current_pos_str = current_pos.to_json(
            #     orient='columns', force_ascii=False)
            if not (current_pos is None):
                current_contract = list(current_pos['vt_symbol'])

                # 有差异的合约
                diff_contract = [
                    x for x in current_contract if x not in __subscribe_list]
                if len(diff_contract) > 0:
                    engine.subscribe(vt_symbols=diff_contract)
                    __subscribe_list.extend(current_contract)
                    sleep(2)

                # # 获取持仓信息： 手数 与 最新价
                # latest_prices = engine.get_ticks(vt_symbols=__subscribe_list, use_df=True)[
                #     ['last_price', 'vt_symbol']]
                # while not latest_prices.all().all():
                #     sleep(0.2)
                #     latest_prices = engine.get_ticks(vt_symbols=__subscribe_list, use_df=True)[
                #         ['last_price', 'vt_symbol']]

                # latest_volumns = current_pos[[
                #     'vt_symbol', 'volume', 'direction']]

                # tmp_df = pd.merge(
                #     left=latest_prices, right=latest_volumns, on='vt_symbol', how='inner')
                # final_df = pd.merge(
                #     left=tmp_df, right=all_contract, on='vt_symbol', how='inner')
                # final_df['mk_value'] = final_df['last_price'] * \
                #     final_df['volume'] * final_df['size']
                # local_mkvalue = final_df['mk_value'].sum()

                # EN calculate

                # final_df['weights'] = final_df['mk_value'] / local_mkvalue

                # s = 0

                # for f in final_df['weights']:
                #     s += f**2
                # if s > 0:
                #     EN_sym = 1 / s

                # return local_mkvalue
                weights =[]
                mkv_li = []

                # option_pnl calculate ; mkv cal
                for ix, row in current_pos.iterrows():
                    if option_picker(row['vt_symbol']):
                        tick = engine.get_tick(row['vt_symbol'])

                        if row['direction'] == Direction.LONG:
                            posdir = 1
                        elif row['direction'] == Direction.SHORT:
                            posdir = -1
                        else:
                            posdir = 0

                        option_pnl += (tick.last_price - row['price']) * \
                            row['volume'] * posdir * \
                            contract_size[row['vt_symbol']]
                        # 这里没考虑过卖出期权的的情况，应该是适合的：卖出期权，权利金到期货账户上,期权账户权益为负
                        option_balance += row['price'] * row['volume'] * \
                            posdir * contract_size[row['vt_symbol']]
                    else:
                        # futures contract
                        tick = engine.get_tick(row['vt_symbol'])

                        tmp_mkv = tick.last_price * \
                            row['volume'] * contract_size[row['vt_symbol']]
                        mkv_li.append(tmp_mkv)
                        if row['direction'] == Direction.LONG:
                            mkv_long += tmp_mkv 
                        elif row['direction'] == Direction.SHORT:
                            mkv_short +=  tmp_mkv

                local_mkvalue = mkv_long + mkv_short
                weights = [i / local_mkvalue for i in mkv_li]

                EN_sym = 1 / sum([i **2 for i in weights])
                

            else:
                local_mkvalue = 0.0

            # risk_ratio
            holding_pnl = sum([a.pnl for (_, a) in current_pos.iterrows()])
            risk_ratio2 = (bal - ava - holding_pnl) / bal
            risk_ratio1 = 1 - ava / bal

            if holding_pnl < 0:
                risk_ratio = risk_ratio1
            else:
                risk_ratio = risk_ratio2

        else:
            # no position holing
            risk_ratio = 0.0
            local_mkvalue = 0.0

        # acc data

        acc_dict = engine.main_engine.engines['oms'].accounts.copy()
        dbmanager.update_account(accounts=acc_dict)

        # basic data
        # pos_dict = engine.main_engine.engines['oms'].positions.copy()
        dbmanager.update_basic(mkv=local_mkvalue,
                               mkv_long=mkv_long,
                               mkv_short=mkv_short,
                               risk_ratio=risk_ratio,
                               EN_sym=EN_sym,
                               pnl=futures_pnl,
                               option_pnl=option_pnl,
                               option_balance=option_balance)

      # order & trade data
        order_dict = engine.main_engine.engines['oms'].orders.copy()
        trade_dict = engine.main_engine.engines['oms'].trades.copy()

        check_timestamp(order_dict)
        check_timestamp(trade_dict)

        tradeTime_TRANS(order_dict)
        tradeTime_TRANS(trade_dict)

        dbmanager.update_order(orderdata=order_dict)
        dbmanager.update_trade(tradedata=trade_dict)

        # 等待x秒进入下一轮
        sleep(10)

    else:

        p = pathlib.Path('./positionRecords')
        fmt_str_ts = '%Y%m%d'

        if p.is_dir():
            pass
        else:
            p.mkdir()

        current_dt = datetime.datetime.now()
        current_time = current_dt.time()

        # save position
        initial_pos = engine.get_all_positions(True)
        if not (initial_pos is None):
            if DAY_END < current_time < NIGHT_START:
                contracts_bool = initial_pos['vt_symbol'].str.contains('&')
                current_pos = initial_pos[~contracts_bool]
                filename = current_dt.strftime(fmt_str_ts)+'.json'
                if current_pos.any().any():
                    current_pos.to_json(p / filename)
                engine.write_log('position recorded...')
