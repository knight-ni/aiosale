import aioclient


async def getdata(client, cp, sdtstr, interval, unitname):
    host = cp.get('host')
    url = 'http://{}/china/mng_rpts?action=SLACMngRpts::vf::summary::GoSummary'.format(host)
    data = {
        "p1_start": sdtstr,
        "p2_start": "",
        "p3_start": "",
        "p4_start": "",
        "p5_start": "",
        "p6_start": "",
        "p7_start": "",
        "p8_start": "",
        "p9_start": "",
        "p10_start": "",
        "p_length": interval,
        "p_unit": unitname,
        "next_pid": "2",
        "action": "SLACMngRpts::vf::summary::GoSummary"
    }
    ac = await aioclient.AioClient(cp).fetch(client, url, data)
    return ac
