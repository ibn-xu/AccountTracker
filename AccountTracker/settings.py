

database_set = {
    'driver': 'influxdb',
    'timezone': 'Asia/Shanghai',
    'port': 0,
    'host': '',
    'database': '',
    'username': '',
    'password': ''

}

product_list = ['jinshan']

product_accounts = {
    'jinshan': [
        'CTP.990175',
    ]
}

product_alarm = {
    'jinshan':'alarm_setting.csv'

}

# csv file is expected to be under account file, path here is absolute path.
acc_folder = {
    'jinshan': 'outsourceData.csv'
}

sector_file = 'AccountTracker/sectors.csv'