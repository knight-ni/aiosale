import asyncio
import os
from configparser import ConfigParser

import aiohttp
import pandas as pd
from styleframe import StyleFrame, Styler, utils

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
path = os.path.split(os.path.realpath(__file__))[0] + r'\Conf\client.cfg'
cp = ConfigParser()
cp.read(path)
cp = cp[mytype]
ac = aioclient.AioClient(cp)
threads = 5
conn = aiohttp.TCPConnector(limit=int(threads))


async def sample_for_summary(tasks=None):
    if tasks is None:
        tasks = []
    starttime = '2014-04-01'
    number = 1
    localunit = unit.day.value
    cookie = await ac.getcookie()
    async with aiohttp.ClientSession(connector=conn, cookies=cookie) as client:
        tasks.append(asyncio.create_task(
            getSummaryData.getdata(client=client, cp=cp, sdtstr=starttime, interval=number, unitname=localunit, )))
        tasks = await asyncio.gather(*tasks)
        frames = [f for f in tasks if f is not None]
        print(frames)


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
    async with aiohttp.ClientSession(connector=conn, cookies=cookie) as client:
        tasks.append(asyncio.create_task(
            getTransactionData.getdata(client=client, cp=cp, sdtstr=starttime, edtstr=stoptime, siteno=siteno,
                                       area_id=area_id, loc_id=loc_id, localunit=localunit)))
        tasks = await asyncio.gather(*tasks)
        frames = [f for f in tasks if f is not None]
        print(frames)


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
    async with aiohttp.ClientSession(connector=conn, cookies=cookie) as client:
        tasks.append(asyncio.create_task(getEventData.getdata(client=client, cp=cp, sdtstr=starttime, edtstr=stoptime,
                                                              event_start_time=event_start_time, draw_id=draw_id,
                                                              event_period=event_period, bet_type=bet_type,
                                                              breakdown=breakdown)))
        tasks = await asyncio.gather(*tasks)
        frames = [f for f in tasks if f is not None]
        print(frames)


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
        alldata.to_excel('test.xlsx', index=None)
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
    indicators = ['Period Start', 'Period End', 'Turnover (RMB)', 'Winnings (RMB)']
    number = 1
    localunit = unit.day.value
    cookie = await ac.getcookie()
    async with aiohttp.ClientSession(connector=conn, cookies=cookie) as client:
        for day in daylst:
            tasks.append(asyncio.create_task(
                summaryHandler.datahandle(client, cp, day, number, localunit, indicators)))
        tasks = await asyncio.gather(*tasks)
        frames = [f for f in tasks if f is not None]
        alldata = pd.concat(frames)
        alldata.to_excel('test.xlsx', index=None)
        # excel_writer = StyleFrame.ExcelWriter('test.xlsx')
        # sf = StyleFrame(alldata)
        # sf.apply_column_style(cols_to_style=alldata.columns.values.tolist(), styler_obj=Styler(number_format="2"), style_header=False, use_default_formats=True, width=None,
        #                    overwrite_default_style=True)
        # sf.to_excel(excel_writer=excel_writer, row_to_add_filters=0, index=True)
        # excel_writer.save()


loop = asyncio.get_event_loop()
#loop.run_until_complete(sample_for_event())
loop.run_until_complete(sample_for_months_eventhandle())
