from influxdb import InfluxDBClient
from .database import DB_TZ, BaseDBManager, Driver
from objects import (
    BasicData,
    TradeData3000,
    OrderData,
    AccountData
)
from .database import DB_TZ


def init(_: Driver, settings) -> BaseDBManager:
    return


class InfluxManager(BaseDBManager):
    '''
    plz update_account,update_basic, update_order, update_trade in order
    '''

    # def __init__(self,host,port, username, password,databse):
    def __init__(self, settings: dict):
        self.influx_client = InfluxDBClient(
            settinga['host'],
            settings['port'],
            settings['username'],
            settings['password'],
            settings['database'])
        self.influx_client.create_database(databse)

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

    def update_account(self, accounts: dict):
        # account data contains balance , frozen and available
        self.account_dict = accounts
        for k, v in accounts.items():
            if k.startswith('CTP'):
                self.acc_name = k
                self.available = v.available
                self.balance = v.balance

    def update_basic(self, balance, mkv, risk_ratio, positions: dict):

        # unable to group positions to accounts...
        EN_sym, EN_sec = self.compute_sector(positions)
        tmp_basic = BasicData(
            balance=balance,
            mkv=mkv,
            risk_ratio=risk_ratio,
            leverage=mkv/balance,
            EN_sym=EN_sym,
            EN_sec=EN_sec,
        )

        d = {
            'measurement': 'account',
            'tags': {
                'account': self.acc_name,
                'type': 'basic'
            },
            'fields': tmp_basic.__dict__
        }

        self.influx_client.write(d)

    def update_order(self, orderdata: dict):
        '''
        simply put all order data in, 
        insert new orders only

        key: vt_orderid
        value: OrderData
        '''
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
                'measurement': 'account',
                'tags': {
                    'account': self.acc_name,
                    'type': 'order'
                },
                'time': DB_TZ.localize(v.datetime),
                'fields': {
                    'vt_symbol': v.vt_symbol,
                    'vt_orderid': v.vt_orderid,
                    'direction': v.direction.value,
                    'offset': v.offset.value,
                    'price': v.price,
                    'volume': v.volume,
                    'traded': v.traded,
                    'status': v.status.value,
                    'reference': v.reference
                }
            }
            json_body.append(d)

        self.influx_client.write_points(json_body)

    def update_trade(self, tradedata: dict):
        '''
        simply put all trades data in, 
        insert new trades only

        key: vt_tradeid
        value: TradeData3000 (add reference )
        '''
        inserting = {}
        for k, v in tradedata.items():
            if v == self.trade_buffer.get(k, 0):
                pass
            else:
                inserting[k] = v
                self.trade_buffer[k] = v

        json_body = []
        for k, v in inserting.items():

            relative_order = self.order_buffer.get(v.vt_orderid, 0)
            if relative_order:
                ref = relative_order.reference
            else:
                ref = ''

            d = {
                'measurement': 'account',
                'tags': {
                    'account': self.acc_name,
                    'type': 'trade'
                },
                'time': DB_TZ.localize(v.datetime),
                'fields': {
                    'symbol': v.vt_symbol,
                    'orderid': v.vt_orderid,
                    'tradeid': v.vt_tradeid,
                    'direction': v.direction.value,
                    'offset': v.offset.value,
                    'price': v.price,
                    'volume': v.volume,
                    'reference': ref,

                }
            }
            json_body.append(d)

        self.influx_client.write_points(json_body)

    def compute_sector(self, positions: dict):
        EN_sym = 0
        EN_sec = 0

        return (
            EN_sym,
            EN_sec,
        )
