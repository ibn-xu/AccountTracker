from influxdb import InfluxDBClient
from datetime import datetime
from .database import DB_TZ, BaseDBManager, Driver
from ..objects import (
    BasicData,
    TradeData3000,
    OrderData,
    AccountData
)


def init(_: Driver, settings) -> BaseDBManager:
    return InfluxManager(settings)


measurement_name_basic = 'account_basic'
measurement_name_trade = 'account_trade'
measurement_name_order = 'account_order'
measurement_name_netvalue = 'product_nv'


class InfluxManager(BaseDBManager):
    '''
    plz update_account,update_basic, update_order, update_trade in scequence
    '''

    # def __init__(self,host,port, username, password,datbase):
    def __init__(self, settings: dict):
        self.influx_client = InfluxDBClient(
            settings['host'],
            settings['port'],
            settings['username'],
            settings['password'],
            settings['database'])
        self.database = settings['database']
        # self.influx_client.create_database(settings['database'])

        self.order_buffer = {}  # save order objects for records
        self.trade_buffer = {}  # save trade objects for records
        self.account_dict = {}  # vt_accountid : AccountData
        self.acc_name = ''
        self.balance = 0
        self.available = 0

    def __del__(self):
        self.influx_client.close()

    def save_data(self):
        pass

    def update_nv(self, product, nv):
        d = {
            'measurement': measurement_name_netvalue,
            'tags': {
                'product': product,
            },
            'fields': {
                'nv': nv
            }
        }

        self.influx_client.write_points([d])

    def update_account(self, accounts: dict):
        # account data contains balance , frozen and available
        self.account_dict = accounts
        for k, v in accounts.items():
            if k.startswith('CTP'):
                self.acc_name = k
                self.available = v.available
                self.balance = v.balance

    def update_basic(self, mkv, mkv_long, mkv_short, risk_ratio, EN_sym=0.0, pnl=0.0, option_pnl=0.0, option_balance=0.0,

                     mkv_agri=0.0,
                     mkv_bond=0.0,
                     mkv_stock=0.0,
                     mkv_metal=0.0,
                     mkv_gold=0.0,
                     mkv_energy=0.0,
                     mkv_black=0.0,



                     ):

        # unable to group positions to accounts...
        tmp_basic = BasicData(
            balance=self.balance,
            mkv=mkv,
            mkv_long=mkv_long,
            mkv_short=mkv_short,
            mkv_agri=mkv_agri,
            mkv_bond=mkv_bond,
            mkv_stock=mkv_stock,
            mkv_metal=mkv_metal,
            mkv_gold=mkv_gold,
            mkv_energy=mkv_energy,
            mkv_black=mkv_black,
            risk_ratio=risk_ratio,
            leverage=mkv/self.balance,
            EN_sym=EN_sym,
            pnl=pnl,
            option_pnl=option_pnl,
            option_balance=option_balance
        )

        d = {
            'measurement': measurement_name_basic,
            'tags': {
                'account': self.acc_name,
            },
            'fields': tmp_basic.__dict__
        }

        self.influx_client.write_points([d])

    def update_order(self, orderdata: dict):
        '''
        simply put all order data in, 
        insert new orders only

        key: vt_orderid
        value: OrderData
        '''
        if orderdata is None:
            return
        inserting = {}

        for k, v in orderdata.items():
            if v == self.order_buffer.get(k, 0):
                pass
            else:
                inserting[k] = v
                self.order_buffer[k] = v

        json_body = []

        for k, v in inserting.items():
            d = {
                'measurement': measurement_name_order,
                'tags': {
                    'account': self.acc_name,
                },
                'time': v.datetime,
                'fields': {
                    'vt_symbol': v.vt_symbol,
                    'vt_orderid': v.vt_orderid,
                    'direction': v.direction.value,
                    'offset': v.offset.value,
                    'price': v.price,
                    'volume': int(v.volume),
                    'traded': v.traded,
                    'status': v.status.value,
                    'reference': v.reference
                }
            }
            json_body.append(d)
        if json_body:
            self.influx_client.write_points(json_body)
            print(f'write {len(json_body)} orders')

    def update_trade(self, tradedata: dict):
        '''
        simply put all trades data in, 
        insert new trades only

        key: vt_tradeid
        value: TradeData3000 (add reference )
        '''
        if tradedata is None:
            return
        inserting = {}
        for k, v in tradedata.items():
            if v == self.trade_buffer.get(k, 0):
                pass
            else:
                inserting[k] = v
                self.trade_buffer[k] = v

        json_body = []
        for k, v in inserting.items():

            related_order = self.order_buffer.get(v.vt_orderid, 0)
            if related_order:
                ref = related_order.reference
            else:
                ref = ''

            d = {
                'measurement': measurement_name_trade,
                'tags': {
                    'account': self.acc_name,
                },
                'time': v.datetime,
                'fields': {
                    'vt_symbol': v.vt_symbol,
                    'vt_orderid': v.vt_orderid,
                    'vt_tradeid': v.vt_tradeid,
                    'direction': v.direction.value,
                    'offset': v.offset.value,
                    'price': v.price,
                    'volume': int(v.volume),
                    'reference': ref,

                }
            }
            json_body.append(d)

        if json_body:
            self.influx_client.write_points(json_body)
            print(f'write {len(json_body)} trades')

    def regular_work(self):
        pass

    def get_nv(self, product_name, start: datetime, end: datetime = datetime.now()):

        start = DB_TZ.localize(start)
        end = DB_TZ.localize(end)

        query_str = ("select * from product_nv"
                     "where product=$product_name"
                     f"and time >= '{start.isoformat()}'"
                     f"and time <= '{end.isoformat()}';"
                     )
        bind_params = {
            "product_name": product_name
        }
        result = self.influx_client.query(query_str, bind_params=bind_params)
        points = result.get_points()

        data = []
        for d in points:
            data.append(d['nv'])
        return data

    def get_pnl(self, account):
        '''
        返回的是[dict]
        '''
        return self.get_data(account, fieldname='pnl', measurement='account_basic')

    def get_optionBalance(self, account):
        '''
        '''
        return self.get_data(account, 'option_balance', 'account_basic')

    def get_data(self, account, fieldname, measurement):
        '''
        return latest data of selected field.
        '''

        query_str = (f"select {fieldname} from {measurement} "
                     f"where account='{account}' and "
                     "time >= now()-15m;"
                     )

        result = self.influx_client.query(query_str)
        points = result.get_points()

        pnlData = []
        for p in points:
            pnlData.append(p[fieldname])

        if pnlData:
            return pnlData[-1]
        else:
            return 0.0
