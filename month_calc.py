import calendar
from datetime import date, datetime


async def cal_month_day(dtstr):
    year, month = dtstr.split('-')
    firstweekday, monthrange = calendar.monthrange(int(year), int(month))
    lastday = date(year=int(year), month=int(month), day=monthrange)
    firstday = '{}-{:0>2s}-{:0>2s}'.format(year, month, '1')
    if firstday=='2013-11-01':
        firstday='2013-11-28'
    lastday = '{}'.format(lastday)
    return [firstday, lastday]


def get_month_range(startmon, endmon):
    startmon = datetime.strptime(startmon, '%Y-%m-%d')
    endmon = datetime.strptime(endmon, '%Y-%m-%d')
    months = (endmon.year - startmon.year) * 12 + endmon.month - startmon.month
    month_range = ['%s-%s' % (startmon.year + mon // 12, mon % 12 + 1) for mon in
                   range(startmon.month - 1, startmon.month + months)]
    return month_range
