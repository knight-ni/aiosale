from datetime import date, datetime, timedelta


def gen_dates(b_date, days):
    day = timedelta(days=1)
    for i in range(days+1):
        yield b_date + day*i


async def get_date_list(start=None, end=None):
    """
    获取日期列表
    :param start: 开始日期
    :param end: 结束日期
    :return:
    """
    sdt = datetime.strptime(start, "%Y-%m-%d")
    edt = datetime.strptime(end, "%Y-%m-%d")
    data = []
    for d in (gen_dates(sdt, (edt-sdt).days)):
        data.append(str(d.year)+'-'+str(d.month).zfill(2)+'-'+str(d.day).zfill(2))
    return data



