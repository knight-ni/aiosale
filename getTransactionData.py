import aioclient


async def getdata(client, cp, sdtstr, edtstr, siteno, area_id, loc_id, localunit):
    host = cp.get('host')
    url = 'http://{}/china/mng_rpts?action=SLACMngRpts::vf::site::GoSearch'.format(host)
    data = {
        "preset_date": "0",
        "start_date": sdtstr,
        "end_date": edtstr,
        "site_no": siteno,
        "geo_area_id": area_id,
        "loc_id": loc_id,
        "breakdown": localunit,
        "download_csv": "0",
        "action": "SLACMngRpts::vf::site::GoRpt"
    }
    ac = await aioclient.AioClient(cp).fetch(client, url, data)
    return ac
