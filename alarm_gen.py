
'''
generate alarm_setting.csv file

只更新1/2，1/4,清盘的条件
分别是： half,quarter,clear
'''
import sys
from enum import Enum
import pandas as pd
from AccountTracker.settings import product_alarm


class ProductType(Enum):
    AGGRESSIVE = 'aggressive'
    PASSIVE = 'passive'


PRODUCTTABLE = {
    'jinshan': ProductType.PASSIVE
}


def __getTarget(nv, product_class: ProductType):
    rtn = nv - 1
    if product_class is ProductType.AGGRESSIVE:
        if rtn < 0:
            return 2.0
        elif rtn <= 0.05:
            return 3.0
        elif rtn <= 0.1:
            return 3.5
        elif rtn <= 0.2:
            return 4.0
        elif rtn <= 0.3:
            return 5.0
        else:
            # rtn > 0.3
            return 6.0
    elif product_class is ProductType.PASSIVE:
        if rtn < 0.05:
            return 2.0
        elif rtn <= 0.1:
            return 2.5
        elif rtn <= 0.15:
            return 3.0
        elif rtn <= 0.2:
            return 3.5
        else:
            # rtn > 0.2
            return 4.0


def update(nv, df: pd.DataFrame, product):
    df = df.copy()
    mdd = __getTarget(nv, PRODUCTTABLE[product]) / 100
    for ix, row in df.iterrows():
        if row['name'] in ('half', 'quarter', 'clear'):
            if row['name'] == 'half':
                tmp_lvl = nv - mdd * 0.49
            elif row['name'] == 'quarter':
                tmp_lvl = nv - mdd * 0.73
            elif row['name'] == 'clear':
                tmp_lvl = nv - mdd * 0.96

            if tmp_lvl <= row['target']:
                # no higher level
                if nv < row['target']:
                    # invalid condition
                    row['type'] = 'hover'
                    df.loc[ix] = row

            else:
                # higher level reached
                row['target'] = tmp_lvl
                # activate alarm
                row['type'] = 'below'
                df.loc[ix] = row

    return df


def reset(nv, df: pd.DataFrame, product):

    mdd = __getTarget(nv, PRODUCTTABLE[product]) / 100
    for ix, row in df.iterrows():
        if row['name'] == 'half':
            row['target'] = nv - mdd * 0.49
            row['type'] = 'below'
        elif row['name'] == 'quarter':
            row['target'] = nv - mdd * 0.73
            row['type'] = 'below'
        elif row['name'] == 'clear':
            row['target'] = nv - mdd * 0.96
            row['type'] = 'below'
        df.loc[ix] = row
    # print(df)
    return df


def testdf(df):
    df = 0


def savedata(filepath, df: pd.DataFrame):
    df.to_csv(filepath, index=False)


if __name__ == "__main__":

    if len(sys.argv) == 1:
        print('''Please specify model:
        ==> update : for updating latest net value, and generate related csv. 
        ==> reset : for start from scrach besed on given net value.
        ''')
        sys.exit()

    # model : update / reset
    mm = sys.argv[1]
    # product name
    product = sys.argv[2]
    nv = float(input("input net value: "))

    alarmfile = product_alarm[product]
    df = pd.read_csv(alarmfile)
    print('*'*50)
    if mm == 'update':
        df = update(nv, df, product)
    elif mm == 'reset':
        df = reset(nv, df, product)

    print(df)
    savedata(alarmfile,df)
