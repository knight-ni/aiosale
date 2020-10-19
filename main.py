# pip install lxml
# pip install html5lib
# pip install xlwt
# pip install openpyxl
import calendar
from datetime import datetime, date
import aiohttp
import pandas as pd
from bs4 import BeautifulSoup
import asyncio
from enum import Enum
import sys

host = '172.30.10.200'
origin = 'http://{}'.format(host)
username = 'NJAGT'
password = 'ab111111'
lang = 'cs'
cookie = 'ADMIN_LANG=lang,{},username,{}; MNG_RPTS_LANG=lang,{},username={}'.format(lang, username, lang, username)
url = 'http://{}/china/mng_rpts'.format(host)
indicators = ['Total Stakes (RMB)', 'Num Tickets']

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 100)


# header = {
#     "Accept-Encoding": "gzip, deflate",
#     "Accept-Language": "zh-CN,zh;q=0.9",
#     "Cache-Control": "max-age=0",
#     "Connection": "keep-alive",
#     "Content-Length": "74",
#     "Content-Type": "application/x-www-form-urlencoded",
#     "Cookie": cookie,
#     "Host": host,
#     "Origin": origin,
#     "Referer": url,
#     "Upgrade-Insecure-Requests": "1",
#     "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
# }

class unit(Enum):
    auto = 'auto'
    event = 'event'
    event_period = 'event_period'
    hour = 'hour'
    day = 'day'
    week = 'week'
    month = 'month'
    quarter = 'quarter'


async def getdata(client, start_date, end_date, interval):
    async def getpara(client):
        async with client.get(url) as resp:
            htmldoc = await resp.text()
            soup = BeautifulSoup(htmldoc, features="html.parser")
            uid = soup.find('input')['value']
            postdata = {
                "uid": uid,
                "username": username,
                "pwd": password,
                "language": lang,
                "action": "GoLogin"
            }
            return postdata

    async with client.post(url, data=await getpara(client)) as resp:
        cookie = resp.cookies

    async with aiohttp.ClientSession(cookies=cookie) as reclient:
        urldata = 'http://{}/china/mng_rpts?action=SLACMngRpts::vf::event::GoSearch'.format(host)
        postdata = {
            "preset_date": "0",
            "start_date": start_date,
            "end_date": end_date,
            "event_start_time": "",
            "draw_id": "",
            "event_period": "any",
            "bet_type": "any",
            "breakdown": interval,
            "action": "SLACMngRpts::vf::event::GoRpt"
        }
        async with reclient.post(urldata, data=postdata) as resp1:
            htmldoc = await resp1.text()
            datasoup = BeautifulSoup(htmldoc, features="html.parser")
            datatab = datasoup.find_all(attrs={'class': 'data'})
            if (len(datatab) > 0):
                df = pd.read_html(str(datatab[1]), index_col='Indicator')[0]
                # order_detail = ['START', 'STOP', 'CS/SGL', 'CS/DBL', 'CS/TBL', 'CS/ACC4', 'CS', 'WDW/DBL', 'WDW/TBL', 'WDW/ACC4', 'WDW', 'TG/DBL', 'TG/TBL', 'TG/ACC4', 'TG', 'HF/DBL', 'HF/TBL', 'HF/ACC4', 'HF', 'Total']
                order = ['CS', 'WDW', 'TG', 'HF', 'Total']

                df['CS'] = df.apply(lambda x: x['CS/SGL'] + x['CS/DBL'] + x['CS/TBL'] + x['CS/ACC4'], axis=1)
                df['WDW'] = df.apply(lambda x: x['WDW/DBL'] + x['WDW/TBL'] + x['WDW/ACC4'], axis=1)
                df['TG'] = df.apply(lambda x: x['TG/DBL'] + x['TG/TBL'] + x['TG/ACC4'], axis=1)
                df['HF'] = df.apply(lambda x: x['HF/DBL'] + x['HF/TBL'] + x['HF/ACC4'], axis=1)
                df1 = df[order]

                df2 = pd.read_html(str(datatab[2]), index_col='Indicator')[0]
                df2['CS'] = df2.apply(lambda x: x['CS'], axis=1)
                df2['WDW'] = df2.apply(lambda x: x['WDW'], axis=1)
                df2['TG'] = df2.apply(lambda x: x['TG'], axis=1)
                df2['HF'] = df2.apply(lambda x: x['HF'], axis=1)
                df1.append(df2)
                frames = [df1, df2]
                newdf = pd.concat(frames)

                dff = pd.Series({'Start Time': start_date, 'Stop Time': end_date})

                for x in indicators:
                    sertmp = newdf.loc[x, :]
                    newidx = {i: x.split(' ')[1] + ' ' + i for i in sertmp.index}
                    sertmp.rename(index=newidx, inplace=True)
                    dff = pd.concat([dff, sertmp])

                np = {key: [dff[key]] for key in dff.index}
                return pd.DataFrame(np)
            else:
                return None


async def cal_month_day(dtstr):
    year, month = dtstr.split('-')
    firstDayWeekDay, monthRange = calendar.monthrange(int(year), int(month))
    lastDay = date(year=int(year), month=int(month), day=monthRange)
    firstday = '{}-{:0>2s}-{:0>2s} 00:00:00'.format(year, month, '1')
    lastday = '{} 23:59:59'.format(lastDay)
    return [firstday, lastday]


def get_month_range(startmon, endmon):
    months = (endmon.year - startmon.year) * 12 + endmon.month - startmon.month
    month_range = ['%s-%s' % (startmon.year + mon // 12, mon % 12 + 1) for mon in
                   range(startmon.month - 1, startmon.month + months)]
    return month_range


async def main(sdtstr, edtstr):
    interval = unit.month.value
    startmon, endmon = datetime.strptime(sdtstr, '%Y-%m-%d'), datetime.strptime(edtstr, '%Y-%m-%d')
    monlst = get_month_range(startmon, endmon)
    tasks = []
    conn = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=conn) as client:
        for mon in monlst:
            start, end = await cal_month_day(mon)
            tasks.append(asyncio.create_task(getdata(client, start, end, interval)))
        tasks = await asyncio.gather(*tasks)
        frames = [f for f in tasks if not f is None]
        alldata = pd.concat(frames)
        alldata.to_excel('test.xlsx', index=None)


loop = asyncio.get_event_loop()
loop.run_until_complete(main('2013-01-01', '2020-10-01'))
