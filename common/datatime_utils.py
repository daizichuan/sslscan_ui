import re
from datetime import datetime
from dateutil import parser


def datetimes_days_interval(day1, day2):
    b2 = (parser.parse(day1) - parser.parse(day2)).days
    print(b2)


def sec_to_data(seconds):
    h = str(int(seconds // 3600 % 24))
    d = str(int(seconds // 86400))
    m = str(int((seconds % 3600) // 60))
    s = str(int(seconds % 60))
    return f'{d}天{h}小时{m}分钟{s}秒'


def expiryDays_sec(expiry_days):
    res = re.match(r'(.*?)天(.*?)小时(.*?)分钟(.*?)秒', expiry_days, re.M | re.I)

    d = int(res.group(1)) * 86400
    h = int(res.group(2)) * 3600
    m = int(res.group(3)) * 60
    s = int(res.group(4))

    res_sec = d + h + m + s
    return res_sec


if __name__ == '__main__':
    day1 = '2037-06-08 14:35:02'
    day2 = '2017-06-08 14:35:02'
    datetimes_days_interval(day1, day2)
