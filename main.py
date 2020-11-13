import asyncio
import os
import time
from configparser import ConfigParser
#not work on Windows Begin
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
#not work on Windows End
import aiohttp
import pandas as pd
import DingTalker
import datetime
import aioclient
import eventHandler
import summaryHandler
import getEventData
import getSummaryData
import getTransactionData
import month_calc
import day_calc
from Classes.myclass import *

mytype = 'report'
path = os.path.split(os.path.realpath(__file__))[0] + r'/Conf/client.cfg'
cp = ConfigParser()
cp.read(path)
cp = cp[mytype]
ac = aioclient.AioClient(cp)
threads = 5


async def sample_for_summary(tasks=None):
    if tasks is None:
        tasks = []
    today = datetime.datetime.today()
    yesday = today - datetime.timedelta(days=1)
    year = yesday.year
    month = yesday.month
    day = yesday.day
    newday = '%04d-%02d-%02d'%(year, month, day)
    number = 1
    localunit = unit.day.value
    indicators = ['Period Start', 'Period End', 'Payout (RMB)']
    cookie = await ac.getcookie()
    conn = aiohttp.TCPConnector(limit=int(threads))
    async with aiohttp.ClientSession(connector=conn, cookies=cookie) as client:
        tasks.append(asyncio.create_task(
                            summaryHandler.datahandle(client, cp, newday, number, localunit, indicators)))
        tasks = await asyncio.gather(*tasks)
        frames = [f for f in tasks if f is not None]
        return frames


async def sample_for_summary_payout(days,tasks=None):
    if tasks is None:
        tasks = []
    today = datetime.datetime.today()
    yesday = today - datetime.timedelta(days=days)
    year = yesday.year
    month = yesday.month
    day = yesday.day
    newday = '%04d-%02d-%02d'%(year, month, day)
    number = days 
    localunit = unit.day.value
    indicators = ['Period Start', 'Period End', 'Winnings (RMB)', 'Collected Winnings (RMB)']
    cookie = await ac.getcookie()
    conn = aiohttp.TCPConnector(limit=int(threads))
    async with aiohttp.ClientSession(connector=conn, cookies=cookie) as client:
        tasks.append(asyncio.create_task(
                            summaryHandler.datahandle(client, cp, newday, number, localunit, indicators)))
        tasks = await asyncio.gather(*tasks)
        frames = [f for f in tasks if f is not None]
        return frames


async def sample_for_transaction(tasks=None):
    if tasks is None:
        tasks = []
    starttime = '2020-10-01'
    stoptime = '2020-10-01'
    siteno = ''
    area_id = ''
    loc_id = ''
    localunit = unit.day.value
    cookie = await ac.getcookie()
    conn = aiohttp.TCPConnector(limit=int(threads))
    async with aiohttp.ClientSession(connector=conn, cookies=cookie) as client:
        tasks.append(asyncio.create_task(
            getTransactionData.getdata(client=client, cp=cp, sdtstr=starttime, edtstr=stoptime, siteno=siteno,
                                       area_id=area_id, loc_id=loc_id, localunit=localunit)))
        tasks = await asyncio.gather(*tasks)
        frames = [f for f in tasks if f is not None]
        return frames


async def sample_for_event(tasks=None):
    if tasks is None:
        tasks = []
    starttime = '2020-10-01 00:00:00'
    stoptime = '2020-10-01 23:59:59'
    event_start_time = ''
    draw_id = ''
    event_period = 'any'
    bet_type = 'any'
    breakdown = unit.month.value
    cookie = await ac.getcookie()
    conn = aiohttp.TCPConnector(limit=int(threads))
    async with aiohttp.ClientSession(connector=conn, cookies=cookie) as client:
        tasks.append(asyncio.create_task(getEventData.getdata(client=client, cp=cp, sdtstr=starttime, edtstr=stoptime,
                                                              event_start_time=event_start_time, draw_id=draw_id,
                                                              event_period=event_period, bet_type=bet_type,
                                                              breakdown=breakdown)))
        tasks = await asyncio.gather(*tasks)
        frames = [f for f in tasks if f is not None]
        return frames


async def sample_for_months_eventhandle(tasks=None):
    startdt, stopdt = '2020-01-01', '2020-12-31'
    if tasks is None:
        tasks = []
    monthlst = month_calc.get_month_range(startdt, stopdt)
    indicators = ['Total Stakes (RMB)', 'Total Winnings (RMB)', 'Num Tickets']
    event_start_time = ''
    draw_id = ''
    event_period = 'any'
    bet_type = 'any'
    breakdown = unit.month.value
    cookie = await ac.getcookie()
    conn = aiohttp.TCPConnector(limit=int(threads))
    async with aiohttp.ClientSession(connector=conn, cookies=cookie) as client:
        for month in monthlst:
            starttime, stoptime = await month_calc.cal_month_day(month)
            starttime = starttime + ' 00:00:00'
            stoptime = stoptime + ' 23:59:59'
            tasks.append(asyncio.create_task(
                eventHandler.datahandle(client, cp, starttime, stoptime, event_start_time, draw_id, event_period,
                                        bet_type, breakdown, indicators)))
        tasks = await asyncio.gather(*tasks)
        frames = [f for f in tasks if f is not None]
        alldata = pd.concat(frames)
        alldata.to_excel('test.xlsx', index=False)
        # excel_writer = StyleFrame.ExcelWriter('test.xlsx')
        # sf = StyleFrame(alldata)
        # sf.apply_column_style(cols_to_style=alldata.columns.values.tolist(), styler_obj=Styler(number_format=utils.number_formats.general_float,horizontal_alignment=utils.horizontal_alignments.center, vertical_alignment=utils.vertical_alignments.center,wrap_text=True,shrink_to_fit=True, fill_pattern_type=utils.fill_pattern_types.solid, indent=0, comment_author=None, comment_text=None, text_rotation=0))
        #                       #, style_header=True, use_default_formats=False, width=None,
        #                       #overwrite_default_style=True)
        # sf.to_excel(excel_writer=excel_writer, row_to_add_filters=0, index=None)
        # excel_writer.save()


async def sample_for_days_summary(tasks=None):
    month = '2020-02'
    startdt, stopdt = await month_calc.cal_month_day(month)
    if tasks is None:
        tasks = []
    daylst = await day_calc.get_date_list(startdt, stopdt)
    indicators = ['Period Start', 'Period End', 'Payout (RMB)']
    number = 1
    localunit = unit.day.value
    cookie = await ac.getcookie()
    conn = aiohttp.TCPConnector(limit=int(threads))
    async with aiohttp.ClientSession(connector=conn, cookies=cookie) as client:
        for day in daylst:
            tasks.append(asyncio.create_task(
                summaryHandler.datahandle(client, cp, day, number, localunit, indicators)))
        tasks = await asyncio.gather(*tasks)
        frames = [f for f in tasks if f is not None]
        alldata = pd.concat(frames)
        alldata.to_excel('test.xlsx', index=False)
        # excel_writer = StyleFrame.ExcelWriter('test.xlsx')
        # sf = StyleFrame(alldata)
        # sf.apply_column_style(cols_to_style=alldata.columns.values.tolist(), styler_obj=Styler(number_format="2"), style_header=False, use_default_formats=True, width=None,
        #                    overwrite_default_style=True)
        # sf.to_excel(excel_writer=excel_writer, row_to_add_filters=0, index=True)
        # excel_writer.save()

async def main(retry):
    tasks = []
    tasks.append(asyncio.create_task(sample_for_summary()))
    tasks.append(asyncio.create_task(sample_for_summary_payout(60)))
    taskres = await asyncio.gather(*tasks)
    frames = [f for f in taskres if f is not None]
    while (len(frames[0])<1 or len(frames[1])<1):
        print("retrying")
        time.sleep(2)
        tasks = []
        tasks.append(asyncio.create_task(sample_for_summary()))
        tasks.append(asyncio.create_task(sample_for_summary_payout(60)))
        taskres = await asyncio.gather(*tasks)
        retry-=1
        frames = [f for f in taskres if f is not None]
        if (retry==0):
            break
    return frames


# #loop.run_until_complete(sample_for_event())
# loop.run_until_complete(sample_for_days_summary())
fes = asyncio.run(main(5))
tab1 = fes[0][0].loc[[0],['Period Start 1','Payout (RMB) 1']]
dt = tab1.iloc[:,0].iloc[0]
year, month, day = dt.split(' ')[0].split('-')
payout = tab1.loc[[0],['Payout (RMB) 1']].iloc[0,-1]
tab2 = fes[1][0].loc[[0],['Period Start 1','Winnings (RMB) 1','Collected Winnings (RMB) 1']]
dt1 = tab2.iloc[:,0].iloc[0]
winning = tab2.iloc[:,1].iloc[0]
collect = tab2.iloc[:,2].iloc[0]
money = round((float(winning) - float(collect))/10000,1)
print('昨日日期:%s\n兑奖金额%s\n60天前日期%s\n中奖奖金%s\n已兑奖金%s\n未兑奖金%s\n'%(dt,payout,dt1,winning,collect,money))
txt = 'e球彩%s月%s日当日全省兑奖金额为%s元; 60天有效兑奖期内未兑奖总额%s万元'%(month, day, payout, money)
dt = DingTalker.DingTalker().sendMsg2(txt)

'''
for f in fes:
    txt = f.loc[[0],['Period Start 1','Payout (RMB) 1']]
    dt = txt.iloc[:,0].iloc[0]
    year, month, day = dt.split(' ')[0].split('-')
    payout = txt.iloc[:,1].iloc[0]
    txt = '%s月%s日,全省兑奖金额为%s元'%(month, day, payout)
    dt = DingTalker.DingTalker().sendMsg2(txt)
dt = DingTalker.DingTalker().sendMsg2()
'''
