import pandas as pd
import time
from tqsdk import TqApi, TqAuth
import datetime
from vnpy.app.option_master.pricing import black_76_cython as black76
import threading
import os
from AccountTracker.database.database_influxdb import init
from AccountTracker.settings import database_set


dbmanager = init(1, database_set)


class NetValue(threading.Thread):

    def __init__(self,stop_epochtime):
        threading.Thread.__init__(self)
        self.stop_epoch = stop_epochtime
        self.read_data()
        self.api = TqApi(None,TqAuth('18516580770','660818'))
        self.quote_list = []
        for _,row in self.df.iterrows():
            self.quote_list.append(self.api.get_quote(row['underlying']))
        self.otc_pre = self.otc_sum('presettle')

    def read_data(self):
        self.df = pd.read_csv('outsourceData.csv',
                              parse_dates=['start', 'end'])
        print(self.df)

    def calcluate_nv(self):
        '''
        compute current net value
        '''
        pnl = self.get_pnl()
        otc_pnl = self.otc_pnl()

        self.current_nv = (
            pnl + otc_pnl + self.df.loc[0]['foreign'] + self.df.loc[0]['total_balance']) / self.df.loc[0]['shares']
        return self.current_nv

    def otc_pnl(self):
        return self.otc_sum() - self.otc_pre

    def otc_sum(self,obj=''):
        if obj == 'presettle':
            price_str = 'pre_settlement'
        else:
            price_str = 'last_price'
        
        pnl_sum = 0.0
        for ix,row in self.df.iterrows():
            price_i = black76.calculate_price(
                getattr(self.quote_list[ix],price_str),
                row['k'],
                0.05,
                row['t'],
                row['v'],
                row['cp'],
                245
            )
            pnl_sum += price_i * row['nominal'] + row['premium']

        return pnl_sum

    def get_pnl(self,account='CTP.990175'):
        '''
        get pnl from influxdb
        '''
        return dbmanager.get_pnl(account)
        

    def save_nv(self):
        # print(self.current_nv)
        dbmanager.update_nv('jinshan',self.current_nv)
    
    def run(self):
        '''
        loop for otc/nv
        '''
        print('开始 净值记录子线程')

        lasttime = datetime.datetime.now().timestamp()
        while self.api.wait_update(self.stop_epoch):
            now = datetime.datetime.now().timestamp()
            if (now - lasttime) > 60:
                self.calcluate_nv()
                self.save_nv()
                lasttime = now
    
    def __del__(self):
        self.api.close()




def run_parent(parent_interval=120,  run_type='sim'):
    # parent thread deciding time to start child thread
    msg = "***************************启动nv数据记录守护父进程****************************"
    print(msg)
    # Chinese futures market trading period (day/night)
    DAY_START = datetime.time(8, 50)
    DAY_END = datetime.time(11, 35)

    DAY_START2 = datetime.time(12, 55)
    DAY_END2 = datetime.time(15, 20)

    NIGHT_START = datetime.time(20, 50)
    NIGHT_END = datetime.time(2, 35)

    current_datetime = datetime.datetime.now()
    current_time = current_datetime.time()
    trading = False
    stop_epochtime = 0
    xx = threading.Thread()
    while True:
        if current_datetime.weekday() in [5, 6]:
            # if weekends, sleep 4 hour
            print('weekends...')
            time.sleep(8*3600)
            current_datetime = datetime.datetime.now()
            current_time = current_datetime.time()
            continue
        # Check whether in trading period
        if (current_time >= DAY_START and current_time < DAY_END):
            trading = True
            stop_dt = datetime.datetime.combine(
                datetime.datetime.today(), DAY_END)
            stop_epochtime = time.mktime(stop_dt.timetuple())

        elif (current_time >= DAY_START2 and current_time < DAY_END2):
            trading = True
            stop_dt = datetime.datetime.combine(
                datetime.datetime.today(), DAY_END2)
            stop_epochtime = time.mktime(stop_dt.timetuple())

        elif (current_time >= NIGHT_START) or (current_time < NIGHT_END):
            trading = True
            stop_dt = datetime.datetime.combine(
                datetime.datetime.today() + datetime.timedelta(1), NIGHT_END)
            stop_epochtime = time.mktime(stop_dt.timetuple())
        else:
            trading = False

        if trading:
            print(f'Expected exit thread time: {stop_dt}')

            if not xx.is_alive():
                # 创建新线程
                xx = NetValue(stop_epochtime)
                os.system('clear')

                # 开启新线程
                xx.start()
                xx.join()
        time.sleep(parent_interval)

        current_datetime = datetime.datetime.now()
        current_time = current_datetime.time()



if __name__ == "__main__":
    run_parent()
