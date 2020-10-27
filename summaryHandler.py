import pandas as pd
import getSummaryData

async def datahandle(client, cp, sdtstr, interval, unitname,
                     indicators):
    dfs = await getSummaryData.getdata(client, cp, sdtstr, interval, unitname)
    if dfs:
        dfs[0].set_index(0, inplace=True)
        #dff = pd.Series({})
        dff = None
        for x in indicators:
            sertmp = dfs[0].loc[x, :]
            newidx = {i: x + ' ' + str(i) for i in sertmp.index}
            sertmp.rename(index=newidx, inplace=True)
            if dff is None:
                dff = sertmp
            else:
                dff = pd.concat([dff, sertmp])

        np = {key: [dff[key]] for key in dff.index}
        return pd.DataFrame(np)
    else:
        return None


