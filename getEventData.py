import aioclient


async def getdata(client, cp, sdtstr, edtstr, event_start_time, draw_id, event_period, bet_type, breakdown):
    host = cp.get('host')
    url = 'http://{}/china/mng_rpts?action=SLACMngRpts::vf::site::GoSearch'.format(host)
    data = {
        "preset_date": "0",
        "start_date": sdtstr,
        "end_date": edtstr,
        "event_start_time": event_start_time,
        "draw_id": draw_id,
        "event_period": event_period,
        "bet_type": bet_type,
        "breakdown": breakdown,
        "action": "SLACMngRpts::vf::event::GoRpt"
    }
    ac = await aioclient.AioClient(cp).fetch(client, url, data)
    return ac
